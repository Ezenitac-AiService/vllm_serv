# Quickstart Validation Guide (028-update-platform-network-profiles)

본 가이드는 하드웨어 사양 보정(RAM 16GB), 서브넷 대역 격리, 동적 VRAM 바인딩, admin_secret 관리, 컨텍스트 스케일링 상한 제어 및 setup.sh non-blocking 연동 검증을 위한 명령어를 제공합니다.

## Prerequisites

- Python 3.11+ 및 `uv` 환경
- 레포지토리 루트 경로: `/home/dev/storage/vllm_serv`

---

## 1. 단위 테스트 수트 실행 (Pytest)

전체 기능 검증을 위해 아래 pytest 테스트를 실행합니다.

```bash
# 1. 플랫폼 프로필(16GB RAM, 서브넷 대역) 검증
uv run pytest tests/unit/test_config_manager_profiles.py tests/unit/test_network_detector.py -v

# 2. 서버 설정(VRAM 동적 바인딩, admin_secret) 검증
uv run pytest tests/unit/test_config_manager.py -v

# 3. 전체 Pytest 수트 실행
uv run pytest
```

---

## 2. setup.sh 원스톱 구축 파이프라인 검증

```bash
# setup.sh 실행하여 CMAKE_ARGS, 방화벽, non-blocking 벤치마크 및 스크립트 생성 검증
./scripts/setup.sh
```

**Expected Outcome**:
- `Platform B` RAM 수치가 16GB로 표시됨.
- `benchmark_context_scaling.py`가 백그라운드/non-blocking으로 1회 실행되어 `config/model_context_profiles.json` 생성.
- 벤치마크 예외 상황 시 파이프라인 중단 없이 경고 후 완료.

---

## 3. OpenAI 규격 HTTP 400 에러 검증 (대형 모델 n_ctx 초과 요청)

```bash
# 1. 서버 구동
./start_server.sh

# 2. gemma4-12b 모델에 허용 상한(4096) 초과 컨텍스트(8192) 요청
curl -s -X POST http://127.0.0.1:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma4-12b",
    "messages": [{"role": "user", "content": "Hello"}],
    "n_ctx": 8192
  }' | python3 -m json.tool
```

**Expected Output**:
```json
{
  "error": {
    "message": "Requested context length (8192) exceeds model maximum allowed context length (4096) for model 'gemma4-12b'.",
    "type": "invalid_request_error",
    "param": "n_ctx",
    "code": "context_length_exceeded"
  }
}
```
