# Implementation Plan: 샘플 스크립트 IP 설정 구조화 및 Reranker API 503 오류 해결 (`078-fix-samples-and-reranker-503`)

**Branch**: `078-fix-samples-and-reranker-503` | **Date**: 2026-08-03 | **Spec**: [`spec.md`](spec.md)

**Input**: Feature specification from `/specs/078-fix-samples-and-reranker-503/spec.md`

## Summary

`samples/common.py` 모듈에서 하드코딩된 특정 IP 주소를 전면 제거하고, `SERVER_HOST` / `OPENAI_BASE_URL` 환경변수 -> `samples/.env` -> `samples/config.json` 순서로 파싱하도록 개선합니다. 
또한 `src/api/routes/inference_api.py` 역방향 프록시 라우터에서 `/v1/rerank` 및 `/v1/embeddings` 요청 수신 시 `auxiliary_manager.ensure_rerank_resident()` 및 `ensure_embedding_resident()`를 온디맨드로 동기화 호출하여 8091 Reranker 백엔드 데몬의 Readiness를 보장함으로써 503 Service Unavailable 오류를 근본적으로 해결합니다.

## Technical Context

**Language/Version**: Python 3.12, FastAPI, Asyncio

**Primary Dependencies**: `httpx`, `pydantic`, `fastapi`, `uv`

**Storage**: Configuration files (`samples/config.json`, `samples/.env`, `samples/config.json.example`)

**Testing**: `pytest`, `httpx` async test client

**Target Platform**: Linux server & client environments (Dev: `10.0.0.x`, Service: `192.168.0.x`)

**Project Type**: Model Serving & Sample API Client Suite

**Performance Goals**: On-demand readiness check within 3.0s; Zero 503 errors

**Constraints**: Zero hardcoded IP addresses in source code; Zero-mock real execution verification

**Scale/Scope**: `samples/common.py`, `samples/config.json.example`, `src/api/routes/inference_api.py`, `tests/integration/test_sample_scripts_and_reranker.py`

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
specs/078-fix-samples-and-reranker-503/
├── plan.md              # Implementation plan
├── research.md          # Technical research & design decisions
├── data-model.md        # Entities & sequence diagram
├── quickstart.md        # Runnable validation guide
├── contracts/           # Interface contracts (sample-config-contract.json)
└── checklists/          # Specification quality checklists (requirements.md)
```

### Target Source Code Layout

```text
samples/
├── common.py                    # Refactored: SERVER_HOST/.env/config.json parsing priority (NO HARDCODED IPs)
├── config.json.example          # Standardized configuration example guide for dev/service networks
├── sample_01_chat.py
├── sample_02_model_params.py
├── sample_03_embedding.py
├── sample_04_reranking.py
└── sample_05_structured_output.py

src/
└── api/
    └── routes/
        └── inference_api.py     # On-demand ensure_rerank_resident & ensure_embedding_resident before proxying

tests/
└── integration/
    └── test_sample_scripts_and_reranker.py  # Integration test for config parsing and /v1/rerank
```

**Structure Decision**: Standard single project layout for `vllm_serv` sample module and API route proxy.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*(No constitution violations. All core principles satisfied.)*
