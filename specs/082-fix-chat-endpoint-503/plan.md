# Implementation Plan: Chat Endpoint 503 Fix & Llama Server Binary Resolution Refactoring

**Branch**: `082-fix-chat-endpoint-503` | **Date**: 2026-08-03 | **Spec**: [`spec.md`](file:///home/dev/storage/vllm_serv/specs/082-fix-chat-endpoint-503/spec.md)

**Input**: Feature specification from `/specs/082-fix-chat-endpoint-503/spec.md`

## Summary

`ProcessManager.verify_and_build_llama_server()`에서 올라마 내장 무효 라이브러리 경로(`/usr/local/lib/ollama/llama-server`)가 탐지되는 부작용을 제거하고, 독립 실행 가능한 C++ `llama-server` 바이너리 또는 Python 서빙 모듈 폴백만 선택하도록 바이너리 탐지 및 검증 로직을 정제합니다. 이를 통해 포트 8089 메인 LLM 백엔드 서빙 엔진(`qwen3.5-4b`)을 크래시 없이 정상 구동하여 `/v1/chat/completions` 엔드포인트의 503 Service Unavailable 회귀 오류를 완치하고 200 OK 인퍼런스를 복구합니다.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, Uvicorn, httpx, llama-cpp-python, C++ llama-server (GGML/CUDA)  
**Storage**: N/A (Process state and memory)  
**Testing**: pytest (`uv run pytest`)  
**Target Platform**: Linux (Ubuntu x86_64, NVIDIA GTX 1080 Ti GPU, CUDA 12.0)  
**Project Type**: web-service & reverse-proxy inference engine  
**Performance Goals**: 503 오류 발생률 0%, 인퍼런스 정상 응답  
**Constraints**: Zero Mock (헌법 II/III조), 전체 회귀 테스트 100% 그린 패스 (헌법 VII조)  
**Scale/Scope**: vllm_serv 백엔드 프로세스 매니저 및 인퍼런스 API 엔드포인트  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책 - 헌법 I조)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙 - 헌법 II조)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_API_CALL=1) 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙 - 헌법 II/III조)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙 - 헌법 IV조)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙 - 헌법 V조)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙 - 헌법 VI조)
- [x] 전체 회귀 테스트 수트 및 Playwright 기반 E2E 브라우저 실측 검증 계획이 포함되어 있는가? (의무적 회귀 테스트 및 브라우저 E2E 검증 원칙 - 헌법 VII조)

## Project Structure

### Documentation (this feature)

```text
specs/082-fix-chat-endpoint-503/
├── plan.md              # Implementation plan (this file)
├── research.md          # Phase 0 research findings
├── data-model.md        # Phase 1 data model & resolution rules
├── quickstart.md        # Phase 1 runnable validation guide
└── contracts/           # Phase 1 API schemas
    └── chat-503-fix-contract.json
```

### Source Code (repository root)

```text
src/
├── core/
│   ├── process_manager.py     # Refine llama-server binary candidate search & execution check
│   ├── llama_manager.py       # Main LLM server process lifecycle
│   └── auxiliary_manager.py   # Rerank & Embedding process isolation
└── api/
    └── routes/
        └── inference_api.py   # Reverse proxy & 503 status code guard

tests/
├── unit/
│   ├── test_process_manager_binary_path.py  # Binary path resolution tests
│   └── test_model_downloader.py             # Model binary verification
└── e2e/
    └── test_dashboard_e2e.py                # Playwright E2E browser tests
```

**Structure Decision**: 기존 `vllm_serv` 단일 시스템 구조(`src/core`, `src/api`, `tests/unit`)를 고수하며 명시적 경로 탐지 및 프로세스 생명주기 분리를 수행합니다.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 없음 | 헌법 원칙 100% 준수 | N/A |
