# Implementation Plan: AI Playground SSE 스트리밍 응답 렌더링 및 Qwen/DeepSeek 사고 과정 파싱 보장 (068-fix-playground-response-streaming)

**Branch**: `068-fix-playground-response-streaming` | **Date**: 2026-07-31 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/068-fix-playground-response-streaming/spec.md)

**Input**: Feature specification from `specs/068-fix-playground-response-streaming/spec.md`

## Summary

본 계획서는 웹 대시보드의 AI Playground에서 Qwen3.5, DeepSeek-R1 등 추론 LLM 모델 이용 시 `<think>` 사고 과정 및 대답 텍스트가 빈 화면으로 남는 문제를 해결하기 위해, `src/api/routes/dashboard_api.py` 내 `run_playground_stream` 파서가 `reasoning_content`, `reasoning`, `content`, `text` 필드를 동적으로 파싱하여 live SSE 스트림으로 UI에 시각화하고 백엔드 가동 상태 점검과 MetricsDB 안전 복구 검증을 수립하는 구현 계획을 정의합니다.

## Technical Context

**Language/Version**: Python 3.11+ (FastAPI, Asyncio)

**Primary Dependencies**: FastAPI, Starlette, httpx, sqlite3, pytest

**Storage**: SQLite (`data/metrics.db` with WAL mode & Lazy Singleton Proxy)

**Testing**: Pytest (`uv run pytest tests/unit/test_dashboard_api.py tests/unit/test_metrics_db.py`)

**Target Platform**: Linux Server (Web Dashboard & LLM Inference Server)

**Project Type**: Web Application & Async Inference Routing

**Performance Goals**: SSE 토큰 전달 지연 최소화 및 100% 정상 파싱

**Constraints**: `uv run` 표준 준수 및 비파괴적 하위 호환성 유지

**Scale/Scope**: `src/api/routes/dashboard_api.py`, `src/core/metrics_db.py`, `tests/unit/test_dashboard_api.py`, `tests/unit/test_metrics_db.py`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_API_CALL=1) 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙)
- [x] 전체 회귀 테스트 수트 검증 계획이 포함되어 있는가? (의무적 회귀 테스트 원칙)

## Project Structure

### Documentation (this feature)

```text
specs/068-fix-playground-response-streaming/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (/speckit-plan command output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── playground-stream-contract.json
└── checklists/
    └── requirements.md  # Specification quality checklist
```

### Source Code (repository root)

```text
src/
├── api/
│   └── routes/
│       └── dashboard_api.py # Enhanced SSE generator parsing reasoning_content, reasoning, text chunks
└── core/
    └── metrics_db.py       # MetricsDB safe lazy singleton initialization

tests/
└── unit/
    ├── test_dashboard_api.py # Unit tests for playground streaming parser and status check
    └── test_metrics_db.py    # Unit tests for database recovery & lazy singleton initialization
```

**Structure Decision**: Standard repository layout modifying dashboard route handlers, metrics database manager, and unit test suites.

## Complexity Tracking

*No violations.*
