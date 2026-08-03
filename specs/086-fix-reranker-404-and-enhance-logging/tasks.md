# Tasks: 리랭커 모델 404 오류 원인 해결 및 프록시/Auxiliary 상세 로깅 고도화

**Input**: Design documents from `/specs/086-fix-reranker-404-and-enhance-logging/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are MANDATORY per Constitution Principle II & VII.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- Single project structure: `src/api/routes/`, `src/core/`, `tests/integration/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify Reranker GGUF model catalog configuration and model file pathing

- [X] T001 Verify Reranker model file pathing and catalog configuration in `config/model_catalog.json` and `src/core/auxiliary_manager.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Port 8091 socket pre-cleanup before spawning Reranker subprocess

- [X] T002 Add `_cleanup_zombie_on_port(8091)` socket force-kill guard before Reranker process spawn in `src/core/auxiliary_manager.py`

---

## Phase 3: User Story 1 - BGE Reranker v2 M3 리랭킹 API 200 OK 성공 (Priority: P1) 🎯 MVP

**Goal**: Ensure `POST /v1/rerank` and `samples/sample_04_reranking.py` return 200 OK and relevance scores without 404 errors.

**Independent Test**: Run `uv run samples/sample_04_reranking.py` and verify HTTP 200 OK response.

### Tests for User Story 1 (MANDATORY)

- [X] T003 [P] [US1] Create integration test verifying Reranker proxy endpoint resolution in `tests/integration/test_sample_scripts_and_reranker.py`

### Implementation for User Story 1

- [X] T004 [US1] Implement Reranker proxy endpoint probing and `/v1/embeddings` cosine similarity fallback adapter in `src/api/routes/inference_api.py` for Python `llama_cpp.server` backend environments

---

## Phase 4: User Story 2 - 404/5xx 프록시 오류 발생 시 상세 로깅 고도화 (Priority: P1)

**Goal**: Record detailed `[RerankerProxyError]` logs with target URL, model status, and multi-line traceback when proxy failures occur.

### Implementation for User Story 2

- [X] T005 [P] [US2] Implement structured `[RerankerProxyError]` logging with target URL, PID, model file status, and multi-line traceback in `src/api/routes/inference_api.py` and `src/core/client_logger.py`

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and regression testing

- [X] T006 [P] Execute quickstart validation guide scenarios in `specs/086-fix-reranker-404-and-enhance-logging/quickstart.md`
- [X] T007 Run regression tests on reranker and sample scripts (`uv run pytest tests/integration/test_sample_scripts_and_reranker.py -v`)

---

## Dependencies & Execution Order

- **Phase 1 (Setup)** -> **Phase 2 (Foundational)** -> **Phase 3 (User Story 1)** -> **Phase 4 (User Story 2)** -> **Phase 5 (Polish)**
