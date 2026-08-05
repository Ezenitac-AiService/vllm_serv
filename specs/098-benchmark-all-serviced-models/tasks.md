---
description: "Task list for feature 098-benchmark-all-serviced-models implementation"
---

# Tasks: 서비스 대상 전체 LLM 모델 기반 컨텍스트 윈도우 스케일링 벤치마크 확장 (Step 4.5 Multi-Model Context Benchmark)

**Input**: Design documents from `/specs/098-benchmark-all-serviced-models/`

**Prerequisites**: [`plan.md`](file:///home/dev/storage/vllm_serv/specs/098-benchmark-all-serviced-models/plan.md) (required), [`spec.md`](file:///home/dev/storage/vllm_serv/specs/098-benchmark-all-serviced-models/spec.md) (required), [`research.md`](file:///home/dev/storage/vllm_serv/specs/098-benchmark-all-serviced-models/research.md), [`data-model.md`](file:///home/dev/storage/vllm_serv/specs/098-benchmark-all-serviced-models/data-model.md), [`contracts/cli-contract.md`](file:///home/dev/storage/vllm_serv/specs/098-benchmark-all-serviced-models/contracts/cli-contract.md)

**Tests**: Tests are MANDATORY per Constitution Principle II & VII. Implementation without failing test verification is strictly prohibited.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Exact file paths included in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and initial structure verification

- [X] T001 Inspect existing benchmark pipeline in `scripts/benchmark_context_window.py` and `scripts/setup.sh`
- [X] T002 Verify initial test environment and baseline execution in `tests/integration/test_benchmark_context_window.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure and data model helpers that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 [P] Add `is_supported` field and profile schema validation helpers in `src/core/config_manager.py`
- [X] T004 [P] Enhance process cleanup helper with SIGKILL fallback in `src/core/process_manager.py`
- [X] T005 [P] Create unit tests for profile schema validation and atomic dictionary merge in `tests/unit/test_config_manager_profiles.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - 카탈로그 내 서비스 대상 전체 LLM 모델의 실측 GPU 벤치마크 및 스케일링 프로파일링 (Priority: P1) 🎯 MVP

**Goal**: `--force-benchmark` 및 `--fine-grained` 실행 시 `config/model_catalog.json` 내 모든 LLM 후보 모델에 대해 실제 GPU 인퍼런스 프로세스를 스폰하여 이진 탐색 스케일링 벤치마크를 순차적으로 구동하고 `config/model_context_profiles.json`에 원자적으로 저장

**Independent Test**: `uv run python scripts/benchmark_context_window.py --force-benchmark` 구동 후 `config/model_context_profiles.json`에 등록된 6개 이상 LLM 모델 전체의 실측 프로필 및 `is_supported` 상태가 정상 수록되는지 단정 검증

### Tests for User Story 1 (MANDATORY) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T006 [P] [US1] Create failing integration test for multi-model real GPU benchmarking in `tests/integration/test_multi_model_benchmark.py`
- [X] T007 [P] [US1] Create failing integration test for 120s timeout and OOM `unsupported` fallback in `tests/integration/test_benchmark_timeout_fallback.py`
- [X] T008 [P] [US1] Create failing unit test for Partial Cache Miss pinpoint sync in `tests/unit/test_partial_cache_miss.py`

### Implementation for User Story 1

- [X] T009 [P] [US1] Implement LLM candidate model extraction helper (`get_candidate_llm_models()`) in `scripts/benchmark_context_window.py`
- [X] T010 [US1] Implement per-model 120s timeout wrapper (`asyncio.wait_for(..., timeout=120)`) and SIGKILL process cleanup in `scripts/benchmark_context_window.py`
- [X] T011 [P] [US1] Implement `unsupported` status assignment (`recommended_context_length=2048`, `is_supported=False`) for OOM/timeout models in `scripts/benchmark_context_window.py`
- [X] T012 [US1] Refactor `evaluate_all_catalog_models()` in `scripts/benchmark_context_window.py` to spawn real GPU processes for all candidate LLM models sequentially
- [X] T013 [US1] Implement Partial Cache Miss detection (`catalog_llm_models - existing_profiles`) and pinpoint sync logic in `scripts/benchmark_context_window.py`
- [X] T014 [US1] Implement atomic profile merge and temporary file replacement (`.tmp` -> `os.replace`) in `save_benchmark_profile()` within `scripts/benchmark_context_window.py`
- [X] T015 [US1] Verify all tests pass in `tests/integration/test_multi_model_benchmark.py`, `tests/integration/test_benchmark_timeout_fallback.py`, and `tests/unit/test_partial_cache_miss.py`

**Checkpoint**: At this point, User Story 1 (MVP) is fully functional and testable independently

---

## Phase 4: User Story 2 - setup.sh 2.8/4.5단계 및 CLI 파라미터와의 일관된 모듈 연동 (Priority: P2)

**Goal**: `./setup.sh --force-benchmark` 및 일반 `./setup.sh` 구동 시 Step 2.8과 Step 4.5에서 다중 모델 실측 벤치마크 및 캐시 고속 스킵이 통합 동작하도록 연동

**Independent Test**: `./setup.sh --force-benchmark` 구동 후 exit 0 확인 및 일반 `./setup.sh` 5초 이내 캐시 스킵 통과 검증

### Tests for User Story 2 (MANDATORY) ⚠️

- [X] T016 [P] [US2] Create failing shell integration test for `./setup.sh --force-benchmark` and cached bypass in `tests/integration/test_setup_benchmark_integration.py`

### Implementation for User Story 2

- [X] T017 [US2] Update Step 2.8 in `scripts/setup.sh` to delegate to `benchmark_context_window.py --force-benchmark` when `--force-benchmark` is set
- [X] T018 [US2] Update Step 4.5 in `scripts/setup.sh` to execute pinpoint cache sync or cached bypass based on `model_context_profiles.json` status
- [X] T019 [US2] Ensure `--skip-benchmark` flag in `scripts/setup.sh` cleanly bypasses Step 2.8 and Step 4.5
- [X] T020 [US2] Verify shell integration tests pass in `tests/integration/test_setup_benchmark_integration.py`

**Checkpoint**: User Story 1 and 2 are fully integrated and independently testable

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation, and regression testing across the entire system

- [X] T021 [P] Run runnable validation scenarios 1~4 in `specs/098-benchmark-all-serviced-models/quickstart.md`
- [ ] T022 Run full regression test suite (`uv run pytest`) per Constitution Principle VII
- [ ] T023 Run E2E Playwright dashboard test suite (`uv run pytest tests/e2e/`) per Constitution Principle VII
- [X] T024 [P] Verify shell script syntax and formatting (`bash -n scripts/setup.sh`)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion (MVP!)
- **User Story 2 (Phase 4)**: Depends on User Story 1 completion
- **Polish (Phase 5)**: Depends on all User Stories completion

### Within Each User Story

- Tests MUST be written first and verified to FAIL before implementation
- Helper methods before pipeline refactoring
- Core logic before CLI/shell script integration

---

## Parallel Opportunities

- **Foundational Phase**: T003, T004, T005 can run in parallel
- **User Story 1 Tests**: T006, T007, T008 can run in parallel
- **User Story 2 Tests**: T016 can run in parallel
- **Polish Phase**: T021 and T024 can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Run `uv run python scripts/benchmark_context_window.py --force-benchmark`
5. Verify `config/model_context_profiles.json` contains full multi-model profiles

### Incremental Delivery

1. Complete Setup + Foundational
2. Implement User Story 1 (MVP) -> Test independently
3. Implement User Story 2 -> Test `setup.sh` integration
4. Run Phase 5 Polish & full regression test suite

---

## Phase 6: Convergence

**Purpose**: Remediation of gaps identified during convergence assessment (2026-08-05)

- [ ] T025 Fix Stage 3 status string assertion mismatch in `tests/unit/test_setup_benchmark_integration.py::test_evaluate_all_catalog_models_force_benchmark`: test expects `"Multi-Model Catalog Forced Benchmark"` but `evaluate_all_catalog_models()` returns `"SUCCESS (Multi-Model Catalog Forced Real GPU Benchmark)"` — update assertion substring to match implementation per DoD-004 (partial)
