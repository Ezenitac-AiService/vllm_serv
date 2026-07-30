# Implementation Plan: 실시간 LLM 백엔드 엔진 연동 Playground & 프롬프트/응답 원문 Payload 캡처 고도화 (046-real-llm-playground-payload)

**Branch**: `046-real-llm-playground-payload`  
**Specification**: [spec.md](file:///home/dev/storage/vllm_serv/specs/046-real-llm-playground-payload/spec.md)  
**Research**: [research.md](file:///home/dev/storage/vllm_serv/specs/046-real-llm-playground-payload/research.md)  
**Data Model**: [data-model.md](file:///home/dev/storage/vllm_serv/specs/046-real-llm-playground-payload/data-model.md)  

---

## Architecture & Touchpoints

1. **Eliminate Mock String in `src/api/routes/dashboard_api.py`**:
   - `run_playground_test` 함수에서 더미 파이프라인 제거.
   - `http://127.0.0.1:8089/v1/chat/completions` C++ backend server 호출 및 실제 response token/completion parsing.
2. **Reverse Proxy Payload Logging (`src/api/routes/inference_api.py`)**:
   - `/v1/*` inference proxy handler에서 actual request body (prompt) 및 response body (completion text) capture하여 `metrics_db.log_request`에 100% 정밀 보장 저장.
3. **Anti-Mock Verification (`tests/unit/test_real_llm_playground_payload.py`)**:
   - 실측 테스트 수트 작성 및 전체 회귀 검증.

---

## Constitution Compliance Check

- [x] Zero Mock Policy in Implementation Code (Constitution v1.5.2)
- [x] All test commands executed via `uv run pytest`.
