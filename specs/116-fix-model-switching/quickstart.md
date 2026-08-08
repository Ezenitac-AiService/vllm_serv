# Quickstart & Validation Guide: 동적 모델 스위칭 (Fix Model Switching)

**Feature**: `fix-model-switching`  
**Feature Directory**: `specs/116-fix-model-switching`  

## 1. 사전 준비 (Prerequisites)

- `vllm_serv` 백엔드 서버 구동:
  ```bash
  ./start_server.sh
  ```
- 서버 상태 확인 (PID 및 READY 상태 검증):
  ```bash
  ./status_server.sh
  ```

---

## 2. 실측 검증 시나리오 (Validation Steps)

### 시나리오 1: httpx 기반 모델 스위칭 샘플 구동
```bash
uv run sample/sample_04_model_switch.py
```
- **기대 결과**: 카탈로그 가용 모델(`qwen3.5-4b`, `qwen3.5-2b` 등)을 순회하며 서버에서 실제 모델 핫스왑이 이루어지고, 각 모델별 생성 답변 및 TPS 결과가 정상 출력됨.

### 시나리오 2: OpenAI SDK 기반 모델 스위칭 샘플 구동
```bash
uv run sample/openai_04_model_switch.py
```
- **기대 결과**: OpenAI SDK 표준 `client.chat.completions.create(model=...)` 호출로 각 모델별 스위칭 및 응답 생성이 정상 처리됨.

### 시나리오 3: 자동화 단체 단위 테스트
```bash
uv run pytest tests/unit/test_inference_api_proxy_headers.py tests/unit/test_llama_manager.py
```
- **기대 결과**: 100% 테스트 통과 (Pass).
