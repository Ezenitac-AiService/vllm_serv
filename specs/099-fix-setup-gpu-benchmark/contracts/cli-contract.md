# CLI & Process Interface Contract: setup.sh 폴리싱 및 GPU 모델 로드 실측 벤치마크 파이프라인 리팩토링 (099-fix-setup-gpu-benchmark)

## 1. 스크립트 CLI 규격

### 1.1 `./setup.sh`

```bash
./setup.sh [--force-benchmark] [--skip-benchmark] [--skip-build] [--wheel-path <PATH>]
```

| 옵션 | 설명 | 동작 방식 |
|:---|:---|:---|
| `--force-benchmark` | 카탈로그 내 모든 LLM 후보 모델 강제 실측 GPU 벤치마크 수행 | Step 0/1 사전 서버 종료 → Step 2.8 카탈로그 전 모델 실측 벤치마크 수행 → Step 4.5 캐시 완비로 5초 스킵 → Step 5 `./start_server.sh` 서빙 복구 |
| `--skip-benchmark` | 3단계 실측 벤치마크 스킵 | 기존 `config/server_config.json` 설정값 보존 |
| (옵션 없음) | 캐시 미스 분점 검증 | `config/model_context_profiles.json` 존재 시 부분 캐시 미스 모델만 핀포인트 벤치마크 |

---

### 1.2 `scripts/benchmark_context_window.py`

```bash
python scripts/benchmark_context_window.py [--force-benchmark] [--skip-benchmark] [--fine-grained] [--model <MODEL_NAME>] [--json]
```

| 옵션 | 설명 | 출력 형식 |
|:---|:---|:---|
| `--force-benchmark` | 카탈로그 내 모든 후보 모델 순차 이진탐색 및 최적 모델 선정 | 터미널 리포트 및 `config/server_config.json`원자적 반영 |
| `--json` | 벤치마크 결과를 JSON 구조체로 stdout 출력 | 표준 JSON 데이터 포맷 |

---

## 2. 백엔드 `llama-server` 프로세스 인자 계약

`ProcessManager.spawn_process(model_name, n_ctx)`가 실행하는 프로세스 파라미터 규격:

```bash
llama-server \
  --model <ABSOLUTE_PATH_TO_GGUF> \
  --host 127.0.0.1 \
  --port 8081 \
  -c <TARGET_N_CTX> \
  -ngl 99 \
  --alias <MODEL_NAME>
```

- `--host 127.0.0.1`: 보안을 위해 로컬 루프백 인터페이스에만 바인딩.
- `-ngl 99`: GPU VRAM 오프로딩 레이어 수 (전체 레이어 오프로딩 지정).
- `--port 8081`: 동적 설정 포트 또는 표준 서빙 포트 지정.

---

## 3. Polling 및 웜업 API 인터페이스 계약

### 3.1 Health Check API (Polling Target)

- **GET** `http://127.0.0.1:8081/health`
- **응답 200 OK**:
```json
{
  "status": "ok"
}
```
- **대기 정책**: 0.2초 간격 비동기 Polling, 최대 10초 내 200 OK 수신 성공 시 웜업 진행.

### 3.2 Warmup Inference API

- **POST** `http://127.0.0.1:8081/v1/chat/completions`
- **Request Body**:
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Warmup inference for KV cache allocation"
    }
  ],
  "max_tokens": 10
}
```
- **Response Body**: Standard OpenAI chat completion format.
- **성공 조건**: HTTP 200 OK 수신 및 생성 속도 TPS > 0.0 산출.
