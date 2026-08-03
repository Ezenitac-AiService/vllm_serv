# Implementation Plan: Reranker API `/v1/rerank` 404 라우팅 오류 해결 (`079-fix-reranker-404-routing`)

**Branch**: `079-fix-reranker-404-routing` | **Date**: 2026-08-03 | **Spec**: [`spec.md`](spec.md)

**Input**: Feature specification from `/specs/079-fix-reranker-404-routing/spec.md`

## Summary

`src/api/routes/inference_api.py`의 `reverse_proxy` 라우터 함수에서 `/v1/rerank` (또는 `/rerank`) 요청 수신 시, 백엔드 8091 포트 데몬으로 전달하는 후보 경로 목록 `["/reranking", "/v1/rerank", "/rerank", "/v1/reranking"]`을 순차적으로 탐색 및 폴백(Path Fallback)하도록 수정하여 `404 Not Found` 라우팅 에러를 근본적으로 해결합니다.

## Technical Context

**Language/Version**: Python 3.12, FastAPI, Asyncio

**Primary Dependencies**: `httpx`, `fastapi`, `uv`

**Storage**: None

**Testing**: `pytest`, `httpx` async test client

**Target Platform**: Linux server & client environments

**Project Type**: Model Serving API Proxy

**Performance Goals**: Sub-5ms path fallback detection; Zero 404 errors

**Constraints**: Zero mock data in production pipeline; Real server integration

**Scale/Scope**: `src/api/routes/inference_api.py`, `tests/integration/test_reranker_404_routing.py`

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
specs/079-fix-reranker-404-routing/
├── plan.md              # Implementation plan
├── research.md          # Technical research & design decisions
├── data-model.md        # Sequence diagram
├── quickstart.md        # Runnable validation guide
├── contracts/           # Interface contracts (reranker-routing-contract.json)
└── checklists/          # Specification quality checklists (requirements.md)
```

### Target Source Code Layout

```text
src/
└── api/
    └── routes/
        └── inference_api.py     # Reverse proxy with multi-candidate backend path fallback for /v1/rerank

tests/
└── integration/
    └── test_reranker_404_routing.py  # Integration test for candidate path fallback logic
```

## Complexity Tracking

*(No constitution violations. All core principles satisfied.)*
