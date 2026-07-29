# Tasks: Real GPU Benchmark Engine & Dual-Mode (Mock vs Real) Automated Test Framework

**Input**: Design documents from `/specs/014-real-gpu-benchmark-testing/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included per TDD and Quality Assurance principles.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- File paths are explicitly specified in all task descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and feature environment verification

- [x] T001 Verify project environment & feature 014 artifacts in specs/014-real-gpu-benchmark-testing/plan.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T002 Add TestExecutionMode and RealGpuBenchmarkSession entities in src/core/process_manager.py and scripts/benchmark_quality.py per data-model.md
- [x] T003 [P] Create contract validator for specs/014-real-gpu-benchmark-testing/contracts/dual-mode-test-schema.json in tests/unit/test_gpu_detector.py
- [x] T004 Implement _verify_and_build_llama_server CMake CUDA build helper (cmake -B build -DGGML_CUDA=ON && cmake --build build) in src/core/process_manager.py (FR-001)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - CUDA LLM 서버 자동 로드 및 실측 인퍼런스 벤치마크 (Priority: P1) 🎯 MVP

**Goal**: Guarantee CUDA llama-server check/build, auto model download from HuggingFace Hub, resident qwen3.5-4b load, and sequential 6-model benchmark loop with 100% failure details recorded into report.

**Independent Test**: Run `python scripts/benchmark_quality.py --auto-download --real` and verify all 6 models (including failures/timeouts) are 100% recorded in generated markdown report.

### Tests for User Story 1

- [x] T005 [P] [US1] Unit test for CUDA llama-server CMake build resolution and model download check in tests/unit/test_model_downloader.py

### Implementation for User Story 1

- [x] T006 [US1] Update ProcessManager.spawn_process to trigger _verify_and_build_llama_server when llama-server binary is missing in src/core/process_manager.py (FR-001)
- [x] T007 [US1] Update run_real_benchmark_loop in scripts/benchmark_quality.py to perform auto-download, sequential 6-model load, real HTTP inference, and report compilation with zero omitted rows (FR-002, FR-003)

**Checkpoint**: User Story 1 fully functional and testable independently (MVP ready!)

---

## Phase 4: User Story 2 - 테스트 코드의 듀얼 모드(Mock Mode vs Real GPU Mode) 분리 (Priority: P1)

**Goal**: Introduce Pytest --real option fixture in tests/conftest.py allowing explicit separation between fast Mock Mode (TEST_MODE=mock) and real CUDA GPU integration testing (pytest --real), prohibiting hardcoded dummy response masking during real mode.

**Independent Test**: Run `uv run pytest tests/integration/ -v --real` to verify real GPU process execution, and `uv run pytest tests/unit/ -v` for Mock Mode unit execution.

### Tests for User Story 2

- [x] T008 [P] [US2] Create dual-mode Pytest option fixture (--real) and test_mode fixture in tests/conftest.py
- [x] T009 [P] [US2] Integration test for Real GPU Mode HTTP inference and healthcheck in tests/integration/test_quality_benchmark.py

### Implementation for User Story 2

- [x] T010 [US2] Update tests/integration/test_gpu_validation.py and tests/integration/test_serving_switch.py to enforce strict real process spawning without mock overrides when --real is active (FR-004, FR-005)

**Checkpoint**: User Stories 1 and 2 work independently.

---

## Phase 5: User Story 3 - Gemma 4 (E2B / E4B / 12B) 및 Qwen 3.5 프로세스 생명주기 안정화 (Priority: P2)

**Goal**: Ensure continuous async stdout/stderr stream drain in ProcessManager so llama-server never deadlocks on 64KB log output during Gemma 4 / Qwen 3.5 model switches.

**Independent Test**: Perform 5 consecutive model switches between Gemma 4 E2B/E4B and Qwen 3.5 4B without socket timeout or process deadlock.

### Tests for User Story 3

- [x] T011 [P] [US3] Integration test for Gemma 4 E2B/E4B async stream drain and serving READY check in tests/integration/test_serving_switch.py

### Implementation for User Story 3

- [x] T012 [US3] Verify ProcessManager._drain_stdout continuous logging task and graceful process termination escalation in src/core/process_manager.py (FR-006)

**Checkpoint**: All user stories functional and complete.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, refactoring, and test suite execution

- [x] T013 [P] Execute full pytest test suite in both Mock Mode (pytest) and Real Mode (pytest --real) verifying zero regressions in tests/
- [x] T014 Execute runnable quickstart validation guide in specs/014-real-gpu-benchmark-testing/quickstart.md


---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS user stories
- **User Stories (Phase 3+)**: Depend on Foundational phase completion
  - Sequential priority order: US1 (P1) → US2 (P1) → US3 (P2)
- **Polish (Phase 6)**: Depends on all user stories completion

### Parallel Opportunities

- T003, T005, T008, T009, T011, T013 marked [P] can run in parallel.
