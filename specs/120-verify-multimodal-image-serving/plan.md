# Implementation Plan: 멀티모달(비전) 모델 로딩 및 이미지 입력 서빙 검증

**Branch**: `120-verify-multimodal-image-serving` | **Date**: 2026-08-08 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/120-verify-multimodal-image-serving/spec.md)

**Input**: Feature specification from `/specs/120-verify-multimodal-image-serving/spec.md`

## Summary

Gemma 4 3종(`gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`)과 신규 `qwen3.5-9b-vision` 멀티모달 모델에 대해 백엔드 인퍼런스 엔진(`llama-server`) 구동 시 비전 프로젝터(`--mmproj`) CLI 파라미터 결합 무결성을 실측 검증하고, 32GB RAM / 11GB VRAM 서버 환경 방어를 위한 25MB HTTP 바디 제한 검증 및 OpenAI API 호환 역방향 프록시(`/v1/chat/completions`) 엔드포인트의 이미지 입력 페이로드 라우팅 테스트 수트를 완성합니다.

## Technical Context

**Language/Version**: Python 3.11, Bash
**Primary Dependencies**: `llama-server` (C++ Backend Inference Engine), `FastAPI`, `httpx`, `pytest`, `uv`
**Storage**: Local JSON Configuration (`config/model_catalog.json`), GGUF Weights & MMProj Projectors (`models/`)
**Testing**: `pytest` (`uv run pytest`)
**Target Platform**: Linux server (**Hardware Tier: 32GB System RAM, 11GB GPU VRAM**)
**Project Type**: LLM/VLM Inference Web Service / Server
**Performance Goals**: `--mmproj` 인자 결합 검증 100% 통과, 25MB 이하 이미지 페이로드 프록시 라우팅 및 25MB 초과 시 HTTP 413 방어 100% 통과
**Constraints**: `requires_mmproj: true` 모델에 대해 `clip_path` 파일 검증 의무화, 25MB Request Body Size Limit, 11GB VRAM 사전 점유 검증
**Scale/Scope**: 멀티모달 모델 4종 대상 프로세스 관리자 및 API 라우터 연동 테스트 수트 확충

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_API_CALL=1) 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙)
- [x] 전체 회귀 테스트 수트 및 Playwright 기반 E2E 브라우저 실측 검증 계획이 포함되어 있는가? (의무적 회귀 테스트 및 브라우저 E2E 검증 원칙)

## Project Structure

### Documentation (this feature)

```text
specs/120-verify-multimodal-image-serving/
├── spec.md              # Feature Specification
├── plan.md              # Implementation Plan (/speckit-plan output)
├── research.md          # Phase 0 output (/speckit-plan output)
├── data-model.md        # Phase 1 output (/speckit-plan output)
├── quickstart.md        # Phase 1 validation guide (/speckit-plan output)
└── contracts/           # Phase 1 interface contracts
    └── multimodal_serving_contract.md
```

### Source Code (repository root)

```text
config/
└── model_catalog.json             # Model catalog with requires_mmproj and clip_path

src/
├── core/
│   ├── process_manager.py         # ProcessManager for --mmproj CLI flag binding
│   └── model_downloader.py        # ModelDownloader for main GGUF and mmproj check
└── api/
    └── routes/
        └── inference_api.py       # OpenAI reverse proxy with 25MB body limit for image_url payloads

tests/
├── unit/
│   └── test_process_manager_multimodal.py   # Multimodal spawn CLI test
└── integration/
    └── test_multimodal_image_payload_proxy.py # Image payload routing and 25MB limit test
```

**Structure Decision**: 기존 `vllm_serv` 아키텍처를 그대로 활용하며, 32GB RAM / 11GB VRAM 서버 방어를 위한 25MB 바디 제한 및 멀티모달 모델 4종에 대한 백엔드 바인딩 및 역방향 프록시 라우팅 단위/통합 테스트 수트를 수립합니다.

## Complexity Tracking

*Constitution Check 위반 사항이 없으므로 N/A 처리합니다.*
