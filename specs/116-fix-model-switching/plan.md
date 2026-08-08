# Implementation Plan: 동적 모델 스위칭(Model Switching) 정상화 및 샘플 연동 개선

**Branch**: `116-fix-model-switching` | **Date**: 2026-08-08 | **Spec**: [`spec.md`](spec.md)

**Input**: Feature specification from `/specs/116-fix-model-switching/spec.md`

## Summary

`POST /v1/chat/completions` 핸들러(`src/api/routes/inference_api.py`)에서 요청 payload의 `model` 파라미터가 현재 VRAM 상주 서빙 중인 모델과 다를 경우, 백엔드 `llama_manager.load_model_with_download(requested_model)`를 자동 호출하여 원자적 핫스왑을 수행하도록 개선합니다. `llama_manager` 내 `asyncio.Lock`을 기반으로 동시 요청 시 서빙 프로세스 교체를 안전하게 직렬화하고, `sample/sample_04_model_switch.py` 및 `sample/openai_04_model_switch.py` 실행 시 실제 모델 교체 및 TPS 실측이 100% 정상 수행되도록 보장합니다.

## Technical Context

**Language/Version**: Python 3.12 (uv 패키지 환경)  
**Primary Dependencies**: FastAPI, Uvicorn, httpx, openai, llama-cpp-python  
**Storage**: Local GGUF Model Artifacts (`/models/`), Config JSON (`sample/config.json`)  
**Testing**: pytest (`uv run pytest tests/unit/`)  
**Target Platform**: Linux server (NVIDIA GPU CUDA 12.0+ / GTX 1070 / RTX 3060)  
**Project Type**: Web service (FastAPI Gateway & llama-server Inference Engine)  
**Performance Goals**: 모델 스위칭 시 VRAM 100% 깔끔 해제 및 신규 모델 100% VRAM 오프로드  
**Constraints**: OOM 방지, `asyncio.Lock`을 통한 핫스왑 직렬화, 기존 API 규격 준수  
**Scale/Scope**: 카탈로그 지원 전 모델 (`qwen3.5-4b`, `qwen3.5-2b`, `gemma4-e4b` 등)  

## Constitution Check

*GATE: Passed Phase 0 research & Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책 준수)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (단위 테스트 `tests/unit/` 검증)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (`uv run sample/openai_04_model_switch.py` 실측 완진)
- [x] 비파괴적 문서 수정 원칙을 준수하는가?
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가?
- [x] 전체 회귀 테스트 수트 검증 계획이 포함되어 있는가?

## Project Structure

### Documentation (this feature)

```text
specs/116-fix-model-switching/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── chat_completions_contract.json
└── tasks.md             # Phase 2 output (to be created by /speckit-tasks)
```

### Source Code (repository root)

```text
src/
├── api/
│   ├── routes/
│   │   ├── inference_api.py    # POST /v1/chat/completions 동적 모델 핫스왑 라우팅
│   │   └── dashboard_api.py
│   └── server.py
└── core/
    ├── llama_manager.py       # LlamaManager load_model_with_download & asyncio.Lock 핫스왑
    └── process_manager.py     # ProcessManager VRAM 해제 및 서브프로세스 관리

sample/
├── sample_04_model_switch.py   # httpx 기반 동적 모델 전환 실측 샘플
└── openai_04_model_switch.py   # OpenAI SDK 기반 동적 모델 전환 실측 샘플

tests/
└── unit/
    └── test_inference_api_proxy_headers.py
```

**Structure Decision**: 기존 `src/api/routes/inference_api.py` 및 `src/core/llama_manager.py`를 확장하여 백엔드 자동 모델 핫스왑을 구현하고, `sample/` 내 스크립트에서 실제 모델 교체가 동작하도록 구성함.

## Complexity Tracking

> **No violations**. Standard architecture and Asyncio Lock pattern used.
