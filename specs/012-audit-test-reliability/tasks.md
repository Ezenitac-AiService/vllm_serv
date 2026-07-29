# Tasks: Codebase Structural Audit & Real-world Test Reliability Verification

**Input**: Design documents from `/specs/012-audit-test-reliability/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are included per TDD and Quality Assurance principles.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- File paths are explicitly specified in all task descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and feature environment verification

- [x] T001 Verify project environment & feature 012 artifacts in specs/012-audit-test-reliability/plan.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T002 Update ProcessLifecycleState entity in src/core/process_manager.py to track strict vram_offloaded_100pct and recovery policies
- [x] T003 [P] Ensure PortCollisionError exception handling and PID extraction utilities in src/core/gpu_detector.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - 구조적 정밀 점검 및 실측 테스트 신뢰성 진단 (Priority: P1) 🎯 MVP

**Goal**: Fix process teardown call order in `spawn_process()` and resolve Python 3.12 `asyncio` event loop deprecation warnings.

**Independent Test**: Verify `spawn_process()` stops previous server and clears port 8081 before checking zombie collision, with 0 event loop warnings.

### Tests for User Story 1

- [x] T004 [P] [US1] Unit test for ProcessManager spawn_process call order in tests/unit/test_process_manager.py
- [x] T005 [P] [US1] Unit test for _run_async Python 3.12 event loop wrapper in tests/unit/test_process_manager.py

### Implementation for User Story 1

- [x] T006 [US1] Refactor spawn_process in src/core/process_manager.py to execute stop_process and _wait_for_port_free before detect_zombie_collision
- [x] T007 [US1] Implement _run_async helper in scripts/benchmark_quality.py to eliminate DeprecationWarning and RuntimeError on event loop close

**Checkpoint**: User Story 1 fully functional and testable independently (MVP ready!)

---

## Phase 4: User Story 2 - 테스트 수트 Mock 환경과 실측 런타임 수렴성 강화 (Priority: P2)

**Goal**: Align Pytest mock environment socket behavior with real runtime socket teardown to eliminate false positive test passes.

**Independent Test**: Verify Pytest fixture teardown releases port 8081 sockets cleanly with 0 leftover background tasks.

### Tests for User Story 2

- [x] T008 [P] [US2] Integration test for Pytest fixture teardown and socket release in tests/integration/test_gpu_validation.py
- [x] T009 [P] [US2] Unit test for PYTEST_CURRENT_TEST socket bypass alignment in tests/unit/test_process_manager.py

### Implementation for User Story 2

- [x] T010 [US2] Refactor _wait_for_port_free and detect_zombie_collision in src/core/process_manager.py for aligned test/real socket teardown behavior
- [x] T011 [US2] Update test fixtures across tests/integration/test_serving_switch.py to ensure explicit await pm.stop_process() teardown

**Checkpoint**: User Stories 1 and 2 work independently without test suite side-effects.

---

## Phase 5: User Story 3 - 6개 모델 실측 GPU 벤치마크 및 골든 데이터셋 무중단 연속 수행 (Priority: P3)

**Goal**: Execute 6-model sequential GPU benchmark loop with Antigravity Gemini 3.6 Flash Golden Dataset generation (10 items in `data/golden_dataset.json`).

**Independent Test**: Run `python scripts/benchmark_quality.py --auto-download --real` and verify 6 models complete sequentially without port collision or VRAM leaks.

### Tests for User Story 3

- [x] T012 [P] [US3] Unit test for Antigravity Gemini 3.6 Flash Golden Dataset generation in tests/unit/test_quality_evaluator.py
- [x] T013 [P] [US3] Integration test for 6-model sequential benchmark loop in tests/integration/test_quality_benchmark.py

### Implementation for User Story 3

- [x] T014 [US3] Synthesize and write 10 representative golden dataset items directly into data/golden_dataset.json via Antigravity AI Agent and integrate local file loader in src/core/quality_evaluator.py
- [x] T015 [US3] Implement strict 4-step sequential pipeline execution (FR-008, FR-009) with 5s exponential backoff socket cleanup in scripts/benchmark_quality.py
- [x] T016 [US3] Integrate try...finally guarded post-benchmark default model restoration (qwen3.5-4b) at end of scripts/benchmark_quality.py

**Checkpoint**: All user stories functional and 6-model benchmark runs with 100% completion.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, refactoring, and test suite execution

- [x] T017 [P] Execute full pytest test suite (74 tests) in tests/ to verify zero remaining regressions
- [x] T018 Execute runnable quickstart validation guide in specs/012-audit-test-reliability/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS user stories
- **User Stories (Phase 3+)**: Depend on Foundational phase completion
  - Sequential priority order: US1 (P1) → US2 (P2) → US3 (P3)
- **Polish (Phase 6)**: Depends on all user stories completion

### Parallel Opportunities

- T003, T004, T005, T008, T009, T012, T013, T017 marked [P] can run in parallel.
