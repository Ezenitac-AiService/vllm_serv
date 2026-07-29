# Tasks: Codebase Refactoring, Modularity & Architecture Optimization

**Input**: Design documents from `/specs/017-codebase-refactoring-cleanup/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (`[US1]`, `[US2]`, `[US3]`, `[US4]`)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and Pydantic v2 dependency validation

- [x] T001 Verify Pydantic v2 and HTTPX dependencies in `pyproject.toml`
- [x] T002 [P] Verify `uv sync` virtual environment and `uv run pytest` runner configuration in `pyproject.toml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core configuration schemas and CIDR security guard that block user story implementation

**⚠️ CRITICAL**: No user story implementation can begin until this phase is complete

- [x] T003 Create Pydantic v2 `ServerConfig`, `ModelCatalogEntry`, and `ModelCatalog` schemas in `src/core/config_manager.py`
- [x] T004 [P] Create `IpSubnetGuard` CIDR filtering helper module in `src/api/middleware/subnet_filter.py`
- [x] T005 [P] Create unit test for Pydantic `ConfigManager` schema validation in `tests/unit/test_config_manager.py`
- [x] T006 [P] Create unit test for IP Subnet CIDR filtering in `tests/unit/test_subnet_filter.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - 하드코딩 전면 제거 및 설정 외부화 검증 (Priority: P1) 🎯 MVP

**Goal**: Remove 100% of hardcoded ports, hosts, timeouts, and catalog dictionaries from Python source files, delegating to `ConfigManager` and JSON config files.

**Independent Test**: `uv run pytest tests/unit/test_config_manager.py -v` verifies 0 hardcoded constants remaining across `src/`.

- [x] T007 [P] [US1] Create unit test for zero hardcoding in `tests/unit/test_config_manager.py`
- [x] T008 [P] [US1] Refactor `config/server_config.json` and `config/model_catalog.json` schema bindings in `src/core/config_manager.py`
- [x] T009 [US1] Remove hardcoded port/host constants from `src/core/process_manager.py` and replace with `ConfigManager`
- [x] T010 [US1] Remove hardcoded port/host constants from `src/core/llama_manager.py` and replace with `ConfigManager`
- [x] T011 [US1] Remove hardcoded catalog dictionary definitions from `src/core/model_downloader.py` and bind to `ConfigManager`
- [x] T012 [US1] Remove hardcoded constants from `src/api/routes/inference_api.py` and bind dynamically to `ConfigManager`

**Checkpoint**: User Story 1 fully functional - zero hardcoding verified independently.

---

## Phase 4: User Story 2 - 계층적 모듈화 및 직관적 추상화 정립 (Priority: P1)

**Goal**: Enforce single directional dependency (`src/api` -> `src/core` -> `src/eval`), eliminate circular imports, and simplify wrapper functions.

**Independent Test**: `uv run pytest tests/unit/test_architecture_modularity.py -v` verifies 0 circular imports and clean layer isolation.

- [x] T013 [P] [US2] Create architecture modularity and circular import test in `tests/unit/test_architecture_modularity.py`
- [x] T014 [US2] Refactor `src/api/server.py` to decouple router initialization from core manager lifecycle
- [x] T015 [US2] Refactor `src/core/process_manager.py` to add Async Context Manager and explicit `close_transport()` for clean loop termination
- [x] T016 [US2] Refactor `src/eval/quality_evaluator.py` to decouple test runner from API router imports

**Checkpoint**: User Stories 1 AND 2 working independently with clean layer boundaries.

---

## Phase 5: User Story 3 - 사설 내부망(192.168.0.x) 전용 보안 접근 제어 (Priority: P2)

**Goal**: Implement CIDR middleware for `192.168.0.0/24` subnet filtering to block unauthorized public IP access.

**Independent Test**: `uv run pytest tests/unit/test_subnet_filter.py -v` verifies 200 OK for `192.168.0.x` and 403 Forbidden for external IPs.

- [x] T017 [P] [US3] Create subnet middleware integration test in `tests/integration/test_subnet_security.py`
- [x] T018 [US3] Implement `SubnetFilterMiddleware` in `src/api/middleware/subnet_filter.py` using `ipaddress.ip_network`
- [x] T019 [US3] Mount `SubnetFilterMiddleware` in `src/api/server.py` with `allowed_subnets` loaded from `ConfigManager`

**Checkpoint**: User Story 3 complete - CIDR subnet security guard enforced.

---

## Phase 6: User Story 4 - RAG 및 Agent 마이크로서비스 연동 고성능 서빙 (Priority: P2)

**Goal**: Optimize HTTP AsyncClient connection pooling and streaming SSE proxy for low-latency RAG & Agent queries.

**Independent Test**: `uv run pytest tests/integration/test_rag_agent_serving.py -v` verifies high-concurrency streaming completion.

- [x] T020 [P] [US4] Create RAG & Agent concurrent streaming test in `tests/integration/test_rag_agent_serving.py`
- [x] T021 [US4] Refactor `src/api/routes/inference_api.py` to use a singleton `httpx.AsyncClient` connection pool from `app.state.http_client`
- [x] T022 [US4] Refactor SSE streaming generator in `src/api/routes/inference_api.py` with client disconnect handling and resource cleanup

**Checkpoint**: All user stories functional independently and end-to-end.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Automation script updates, documentation alignment, and end-to-end validation

- [x] T023 [P] Update `scripts/setup.sh`, `scripts/start_server.sh`, `scripts/stop_server.sh`, `scripts/status_server.sh` to use `ConfigManager` parameters
- [x] T024 Update `README.md` with CIDR subnet security guidelines and refactored architecture diagram
- [x] T025 Run full test suite `uv run pytest -v` and validate `quickstart.md` scenarios

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories.
- **User Stories (Phases 3-6)**: All depend on Foundational phase completion.
  - Phase 3 (US1, P1) → Phase 4 (US2, P1) → Phase 5 (US3, P2) → Phase 6 (US4, P2).
- **Polish (Phase 7)**: Depends on all user stories being complete.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) and Phase 2 (Foundational).
2. Complete Phase 3 (User Story 1 - Zero Hardcoding).
3. **VALIDATE**: Run `uv run pytest tests/unit/test_config_manager.py -v`.

### Incremental Delivery

1. Foundation ready (Phase 1 + 2).
2. Add US1 → Zero Hardcoding → Validate MVP.
3. Add US2 → Modularity & Async Cleanup → Validate.
4. Add US3 → Subnet Security (`192.168.0.x`) → Validate.
5. Add US4 → RAG & Agent Connection Pool → Validate.
6. Run Polish (Phase 7) & Quickstart guide.
