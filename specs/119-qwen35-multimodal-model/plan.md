# Implementation Plan: Qwen 3.5 9B 멀티모달 모델 검증 및 별도 카탈로그 등록

**Branch**: `119-qwen35-multimodal-model` | **Date**: 2026-08-08 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/119-qwen35-multimodal-model/spec.md)

**Input**: Feature specification from `/specs/119-qwen35-multimodal-model/spec.md`

## Summary

허깅페이스 `unsloth/Qwen3.5-9B-GGUF` 모델의 멀티모달(비전) 지원 사양을 확인하고, 기존 운영 중인 `qwen3.5-9b` 텍스트 전용 카탈로그 항목의 하위 호환성을 유지하면서, 비전 프로젝터(`mmproj-BF16.gguf`)가 결합된 `qwen3.5-9b-vision` 신규 카탈로그 항목을 `config/model_catalog.json`에 추가하고 이에 대한 회귀 검증 수트를 수립합니다.

## Technical Context

**Language/Version**: Python 3.11, Bash
**Primary Dependencies**: `llama-server` (C++ Backend Inference Engine), `pytest`, `uv`
**Storage**: Local JSON Configuration (`config/model_catalog.json`), GGUF Weight Files (`models/qwen3.5-9b-vision/`)
**Testing**: `pytest` (`uv run pytest`)
**Target Platform**: Linux server (CUDA / GPU Acceleration)
**Project Type**: LLM/VLM Inference Web Service / Server
**Performance Goals**: 카탈로그 검증 100% 통과, 기존 `qwen3.5-9b` 운영 서비스 장애 제로(Zero Downtime)
**Constraints**: 기존 `qwen3.5-9b` 텍스트 전용 항목 완전 보존, `requires_mmproj: true` 시 `clip_filename` 및 `clip_path` 설정 의무화
**Scale/Scope**: 신규 카탈로그 엔트리 1개 추가 및 모델 파싱/동기화 스크립트 무결성 검증

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
specs/119-qwen35-multimodal-model/
├── spec.md              # Feature Specification
├── plan.md              # Implementation Plan (/speckit-plan output)
├── research.md          # Phase 0 output (/speckit-plan output)
├── data-model.md        # Phase 1 output (/speckit-plan output)
├── quickstart.md        # Phase 1 validation guide (/speckit-plan output)
└── contracts/           # Phase 1 interface contracts
    └── model_catalog_contract.md
```

### Source Code (repository root)

```text
config/
├── model_catalog.json             # Model catalog registry (Target file to update)
├── model_config.json              # Active model configuration
└── model_context_profiles.json    # Context profile mappings

scripts/
├── ensure_models.py               # Model download & verification script
└── start_server.sh                # Server startup script with --mmproj binding

tests/
├── unit/                          # Catalog & module unit tests
└── e2e/                           # Browser & server integration tests
```

**Structure Decision**: 기존 `vllm_serv` 단일 프로젝트 구조를 활용하며, `config/model_catalog.json` 항목 추가 및 연동 테스트 수트 검증을 수행합니다.

## Complexity Tracking

*Constitution Check 위반 사항이 없으므로 N/A 처리합니다.*
