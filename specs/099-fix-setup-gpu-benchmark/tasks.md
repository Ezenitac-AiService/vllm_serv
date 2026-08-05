---
description: "Task list for feature 099-fix-setup-gpu-benchmark implementation"
---

# Tasks: setup.sh 폴리싱 및 GPU 모델 로드 실측 벤치마크 파이프라인 리팩토링 (099-fix-setup-gpu-benchmark)

**Input**: Design documents from `/specs/099-fix-setup-gpu-benchmark/`

**Prerequisites**: [`plan.md`](file:///home/dev/storage/vllm_serv/specs/099-fix-setup-gpu-benchmark/plan.md) (required), [`spec.md`](file:///home/dev/storage/vllm_serv/specs/099-fix-setup-gpu-benchmark/spec.md) (required), [`research.md`](file:///home/dev/storage/vllm_serv/specs/099-fix-setup-gpu-benchmark/research.md), [`data-model.md`](file:///home/dev/storage/vllm_serv/specs/099-fix-setup-gpu-benchmark/data-model.md), [`contracts/cli-contract.md`](file:///home/dev/storage/vllm_serv/specs/099-fix-setup-gpu-benchmark/contracts/cli-contract.md), [`quickstart.md`](file:///home/dev/storage/vllm_serv/specs/099-fix-setup-gpu-benchmark/quickstart.md)

**Tests**: Tests are MANDATORY per Constitution Principle II & VII. Implementation without failing test verification is strictly prohibited.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Exact file paths included in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and initial benchmark pipeline verification

- [x] T001 Inspect existing benchmark & process manager files in `scripts/benchmark_context_window.py`, `src/core/process_manager.py`, and `scripts/setup.sh`
- [x] T002 Verify test environment and initial baseline execution in `tests/unit/test_setup_benchmark_integration.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure for process spawning, security loopback binding, and signal cleanup that MUST be complete before user story work

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 [P] Add `--host 127.0.0.1` and `-ngl 99` default arguments to `llama-server` process spawn logic in `src/core/process_manager.py`
- [x] T004 [P] Add `signal` (SIGINT/SIGTERM) and `atexit` handlers calling `force_kill_zombie_llama_servers()` in `src/core/process_manager.py`
- [x] T005 [P] Create unit tests for `/health` polling helper and process cleanup in `tests/unit/test_process_manager_health.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - 카탈로그 내 모든 LLM 모델의 실체적 GPU 프로세스 스폰 및 VRAM 로드/인퍼런스 실측 보장 (Priority: P1) 🎯 MVP

**Goal**: GPU 레이어 오프로딩(`-ngl 99`), `/health` Polling, Warmup POST 및 실측 TPS/VRAM 로딩 보장

**Independent Test**: `./setup.sh --force-benchmark` 실행 중 nvtop 또는 nvidia-smi 모니터링 시 각 모델별로 GPU VRAM 점유량 상승 및 GPU Util 점유가 관측되고, 벤치마크 완료 후 `config/model_context_profiles.json` 내 지원 가능 모델들의 `is_supported`가 `true`로 수록되며 `tpot_tok_per_sec`가 0.0 초과의 실측치로 저장되는지 검증

### Tests for User Story 1 (MANDATORY) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T006 [P] [US1] Create failing integration test for `/health` polling ready check and real GPU warmup in `tests/integration/test_gpu_spawn_warmup.py`
- [x] T007 [P] [US1] Create failing unit test for `is_supported` positive TPS profile recording in `tests/unit/test_positive_tps_profile.py`

### Implementation for User Story 1

- [x] T008 [US1] Implement async `/health` polling helper (`poll_server_health(port, timeout=10.0, interval=0.2)`) using `httpx` in `src/core/process_manager.py`
- [x] T009 [US1] Refactor `_execute_single_binary_search_inner()` in `scripts/benchmark_context_window.py` to call `/health` polling before sending `/v1/chat/completions` warmup POST
- [x] T010 [US1] Ensure proper model GGUF file path resolution and `-ngl 99` flag passing in `scripts/benchmark_context_window.py` and `src/core/process_manager.py`
- [x] T011 [US1] Verify all tests pass in `tests/integration/test_gpu_spawn_warmup.py` and `tests/unit/test_positive_tps_profile.py`

**Checkpoint**: At this point, User Story 1 (MVP) is fully functional and testable independently

---

## Phase 4: User Story 2 - setup.sh 내 이중 강제 벤치마크 호출 제거 및 중복 구동 방지 (Priority: P2)

**Goal**: Step 2.8에서 카탈로그 전체 모델 벤치마크 완료 시 Step 4.5에서 무필요한 재벤치마크를 건너뛰고 5초 이내 고속 통과(Smart Skip)

**Independent Test**: `./setup.sh --force-benchmark` 구동 시 Step 2.8에서 전체 실측 벤치마크가 수행된 후 Step 4.5에서는 "캐시 프로필 완비"로 감지하여 5초 이내에 추가 재벤치마킹 없이 완료되는지 로그를 검증

### Tests for User Story 2 (MANDATORY) ⚠️

- [x] T012 [P] [US2] Create failing shell integration test for `./setup.sh --force-benchmark` Step 4.5 smart skip behavior in `tests/integration/test_setup_smart_skip.py`

### Implementation for User Story 2

- [x] T013 [US2] Refactor Step 4.5 in `scripts/setup.sh` to check `config/model_context_profiles.json` cache freshness after Step 2.8 and bypass duplicate `--force-benchmark` execution
- [x] T014 [US2] Verify shell integration tests pass in `tests/integration/test_setup_smart_skip.py`

**Checkpoint**: User Story 1 and 2 are fully integrated and independently testable

---

## Phase 5: User Story 3 - 프로세스 스폰 에러 진단 로그 강화, 사전 정리 및 서빙 복구 (Priority: P3)

**Goal**: Step 0/1 사전 서버 종료, `[BENCHMARK WARN]` 상세 로그 출력, Step 5 서빙 복구(`./start_server.sh`)

**Independent Test**: 의도적으로 포트를 점유시키거나 미존재 모델 경로로 벤치마크 구동 시 명확한 진단 로그가 출력되고 `setup.sh` 완납 후 `./start_server.sh`가 자동 구동되는지 검증

### Tests for User Story 3 (MANDATORY) ⚠️

- [ ] T015 [P] [US3] Create failing unit/integration test for pre-execution server cleanup and fallback profile warning in `tests/integration/test_pre_cleanup_and_restore.py`

### Implementation for User Story 3

- [ ] T016 [US3] Add pre-execution server cleanup (stop existing `llama-server` / FastAPI processes occupying port 8081) in Step 0/Step 1 of `scripts/setup.sh`
- [ ] T017 [US3] Enhance `_record_unsupported_fallback_profile()` in `scripts/benchmark_context_window.py` to print `[BENCHMARK WARN]` with detailed failure reasons and set `is_supported=false`, `scaling_tested=false`, `recommended_context_length=2048`
- [ ] T018 [US3] Add automatic server restoration (`./start_server.sh`) and health check verification in Step 5 of `scripts/setup.sh`
- [ ] T019 [US3] Verify tests pass in `tests/integration/test_pre_cleanup_and_restore.py`

**Checkpoint**: All user stories are fully implemented and independently testable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation, and regression testing across the entire system

- [ ] T020 [P] Run runnable validation scenarios 1~4 in `specs/099-fix-setup-gpu-benchmark/quickstart.md`
- [ ] T021 Run full regression test suite (`uv run pytest`) per Constitution Principle VII
- [ ] T022 Run E2E Playwright dashboard test suite (`uv run pytest tests/e2e/`) per Constitution Principle VII
- [ ] T023 [P] Verify shell script syntax and formatting (`bash -n scripts/setup.sh`)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion (MVP!)
- **User Story 2 (Phase 4)**: Depends on User Story 1 completion
- **User Story 3 (Phase 5)**: Depends on User Story 1 & 2 completion
- **Polish (Phase 6)**: Depends on all User Stories completion

### Within Each User Story

- Tests MUST be written first and verified to FAIL before implementation
- Process & helper methods before pipeline refactoring
- Core logic before CLI/shell script integration

---

## Parallel Opportunities

- **Foundational Phase**: T003, T004, T005 can run in parallel
- **User Story 1 Tests**: T006, T007 can run in parallel
- **User Story 2 Tests**: T012 can run in parallel
- **User Story 3 Tests**: T015 can run in parallel
- **Polish Phase**: T020 and T023 can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Run `uv run python scripts/benchmark_context_window.py --force-benchmark`
5. Verify nvtop shows real GPU VRAM load and positive TPS values (> 0.0)

### Incremental Delivery

1. Complete Setup + Foundational
2. Implement User Story 1 (MVP) -> Test independently
3. Implement User Story 2 -> Test `setup.sh` Smart Skip
4. Implement User Story 3 -> Test pre-cleanup, diagnostic logs & `./start_server.sh` restoration
5. Run Phase 6 Polish & full regression test suite
