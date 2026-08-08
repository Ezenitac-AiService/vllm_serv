# Quickstart & Validation Guide: sample 예제 스크립트 호출 모델 대 응답 모델 일치성 검증 및 하드코딩 제거

**Feature**: `verify-sample-model-response`  
**Feature Directory**: `specs/117-verify-sample-model-response`  

---

## 1. 사전 준비 (Prerequisites)

- `vllm_serv` 백엔드 서버 구동 (개발 IP `10.0.0.41` / 배포 IP `192.168.0.175` / `127.0.0.1`):
  ```bash
  ./start_server.sh
  ```
- MOCK 서버 모드로 빠른 검증 시:
  ```bash
  export MOCK_LLAMA_SERVER=1
  ```

---

## 2. 실측 및 테스트 검증 시나리오 (Validation Scenarios)

### 시나리오 1: httpx 기반 실습 스크립트 모델 교차 검증
```bash
uv run python sample/sample_04_model_switch.py
```
- **기대 결과**: 콘솔 출력에 `[모델 검증: 요청(X) == 응답(X) ✅]` 태그가 각 모델 순회마다 표출되며, 호출 모델과 응답 모델이 100% 일치함을 시각적으로 확인.

### 시나리오 2: OpenAI SDK 기반 실습 스크립트 모델 교차 검증
```bash
uv run python sample/openai_04_model_switch.py
```
- **기대 결과**: OpenAI SDK 표준 응답 `completion.model`과 요청 모델 ID가 100% 일치하며 검증 성공 로그 표출.

### 시나리오 3: sample/ 소스 코드 하드코딩 매직 넘버/IP 0건 검증 및 단위 테스트
```bash
uv run pytest tests/unit/test_sample_model_switch.py
```
- **기대 결과**:
  1. `sample/` 폴더 파이썬 소스 코드 내 하드코딩 IP/포트/목업 텍스트 존재 검사 100% PASS (0건)
  2. 요청 모델 대 응답 모델 교차 검증 단정문 100% PASS
