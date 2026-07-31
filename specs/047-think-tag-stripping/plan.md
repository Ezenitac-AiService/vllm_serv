# Implementation Plan: LLM 응답 내 <think> 추론 태그 자동 파싱 및 정제 (047-think-tag-stripping)

**Branch**: `047-think-tag-stripping` | **Date**: 2026-07-30 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/047-think-tag-stripping/spec.md)

**Input**: Feature specification from `/specs/047-think-tag-stripping/spec.md`

## Summary

DeepSeek R1 / Qwen 2.5/3.5 등 추론 모델의 응답 텍스트에 포함된 `<think>...</think>` 사고과정 태그를 최종 대답 본문에서 자동 정제(Strip) 및 분리하여 `text` 필드에는 깨끗한 최종 답변만 표출하고, 추론 과정은 `thinking_process` 전용 필드로 분리 저장하며, 기본 `max_tokens`를 1024로 상향 조정합니다.

## Technical Context

**Language/Version**: Python 3.12 (uv package manager)

**Primary Dependencies**: FastAPI, httpx, pydantic, sqlite3

**Storage**: SQLite (`data/metrics.db`)

**Testing**: pytest (`uv run pytest`)

**Target Platform**: Linux server (vllm_serv)

**Project Type**: web-service (FastAPI + C++ llama-server backend)

**Performance Goals**: `<think>` 태그 정제 및 파싱 오버헤드 <1ms

**Constraints**: Zero Mock Policy in Implementation Code (Constitution v1.5.2)

**Scale/Scope**: AI Playground, Reverse Proxy (`/v1/*`), Audit Payload Viewer

## Constitution Check

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_API_CALL=1) 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙)

## Project Structure

### Documentation (this feature)

```text
specs/047-think-tag-stripping/
├── plan.md              # Implementation Plan
├── research.md          # Technical research & choices
├── data-model.md        # Data models & schemas
├── quickstart.md        # Validation & verification guide
├── contracts/           # API contracts
│   └── playground_api_contract.md
└── checklists/
    └── requirements.md
```

### Source Code Touchpoints

```text
src/
├── core/
│   ├── think_tag_parser.py   # Helper module for parsing <think>...</think> tags & streaming
│   └── metrics_db.py         # SQLite logging for prompt_text, completion_text & thinking_text
├── api/routes/
    ├── dashboard_api.py      # PlaygroundRequest max_tokens default 1024 & thinking_process field
    └── inference_api.py      # Reverse proxy streaming/non-streaming think tag parsing

tests/unit/
└── test_think_tag_stripping.py # Anti-mock unit test suite
```

**Structure Decision**: Single project layout under `src/` and `tests/unit/`.
