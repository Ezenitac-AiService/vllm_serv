# Tasks: 보조 모델 크래시 루프 방지 및 프록시 503 게이트 (`080-fix-reranker-aux-crash-loop`)

**Input**: Design documents from `/specs/080-fix-reranker-aux-crash-loop/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: TDD approach with explicit unit, integration, and full suite regression tests per Constitution Principle II & VII.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2)
- Exact file paths included in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify feature workspace and initial prerequisites

- [x] T001 Verify design artifacts and setup configuration in `specs/080-fix-reranker-aux-crash-loop/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core enum and configuration extensions that MUST be complete before user stories can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 Add `DISABLED` status enum value to `ProcessStatusEnum` in `src/core/process_manager.py`
- [x] T003 Add `auxiliary_max_crashes` (default: 3) configuration option to `ConfigManager` in `src/core/config_manager.py`

**Checkpoint**: Core enums and configs ready - user story implementation can now begin

---

## Phase 3: User Story 1 - 보조 모델 크래시 무한 루프 차단 및 순차 초기화 (Priority: P1) 🎯 MVP

**Goal**: 보조 모델 프로세스가 VRAM 부족으로 반복 크래시할 때 최대 3회 연속 크래시 후 DISABLED 상태로 전이하여 무한 재시작 루프를 차단하고, 구동 초기화 시 Embedding 후 Rerank를 순차 구동하여 피크 VRAM 합산을 예방합니다.

**Independent Test**: `uv run pytest tests/unit/test_auxiliary_circuit_breaker.py tests/unit/test_auxiliary_sequential_init.py -v`

### Tests for User Story 1 (MANDATORY) ⚠️

- [x] T004 [P] [US1] Create unit tests for circuit breaker (3 consecutive crashes -> DISABLED, crash counter reset on READY) in `tests/unit/test_auxiliary_circuit_breaker.py`
- [x] T005 [P] [US1] Create unit tests for sequential initialization (Embedding READY check before starting Reranker) in `tests/unit/test_auxiliary_sequential_init.py`

### Implementation for User Story 1

- [x] T006 [US1] Implement consecutive crash tracking (`embedding_consecutive_crashes`, `rerank_consecutive_crashes`), circuit breaker (`ProcessStatusEnum.DISABLED` transition after max crashes), and reset on READY in `src/core/auxiliary_manager.py`
- [x] T007 [US1] Update `start_auto_startup_and_recovery()` to initialize Embedding and Reranker sequentially (wait for Embedding status before launching Reranker) in `src/core/auxiliary_manager.py`

**Checkpoint**: User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - 보조 모델 READY 대기 후 프록시 전달 보장 (Priority: P1)

**Goal**: `reverse_proxy`에서 `/v1/rerank` 및 `/v1/embeddings` 요청 수신 시 `ensure_*_resident`의 반환 상태가 READY인 경우만 프록시 전달하고, DISABLED 또는 ERROR 상태인 경우 백엔드 전달 없이 즉시 503 Service Unavailable 및 명확한 에러 메시지를 반환합니다.

**Independent Test**: `uv run pytest tests/integration/test_auxiliary_503_gate.py -v`

### Tests for User Story 2 (MANDATORY) ⚠️

- [x] T008 [P] [US2] Create integration tests for reverse proxy 503 gate (verify 503 response on DISABLED/ERROR state, no 404 response, 200 on READY) in `tests/integration/test_auxiliary_503_gate.py`

### Implementation for User Story 2

- [x] T009 [US2] Update `reverse_proxy` in `src/api/routes/inference_api.py` to validate `ProcessState.status` after `ensure_*_resident` calls and raise `HTTPException(status_code=503)` if status is not READY or if DISABLED

**Checkpoint**: User Stories 1 AND 2 are both functional and independently testable.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Validation and full suite regression testing per Constitution Principle VII

- [x] T010 [P] Validate execution scenarios documented in `specs/080-fix-reranker-aux-crash-loop/quickstart.md`
- [x] T011 Run full regression test suite (`uv run pytest tests/ -v`) to guarantee zero regression across all endpoints

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion (T002, T003)
- **User Story 2 (Phase 4)**: Depends on Foundational phase completion (T002, T003) and US1 state model
- **Polish (Phase 5)**: Depends on US1 and US2 implementation complete

### Parallel Opportunities

- T004 [US1] and T005 [US1] tests can be written in parallel
- T008 [US2] tests can be created in parallel with US1 work
- T010 can run in parallel with T011

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & Phase 2 (T001 - T003)
2. Complete Phase 3 User Story 1 (T004 - T007)
3. Validate User Story 1 with unit tests

### Full Delivery

1. Complete Phase 4 User Story 2 (T008 - T009)
2. Complete Phase 5 Polish & Full Suite Regression (T010 - T011)
