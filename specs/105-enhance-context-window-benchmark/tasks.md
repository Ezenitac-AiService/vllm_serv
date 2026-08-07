# Tasks: 컨텍스트 윈도우 크기 벤치마킹 고도화 및 헬스체크/초기화 진단 개선 (105-enhance-context-window-benchmark)

**Input**: Design documents from `/specs/105-enhance-context-window-benchmark/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/cli-contract.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- File paths are exact and relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project environment initialization and prerequisite verification

- [ ] T001 Verify python environment and project dependencies using `uv sync`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: Core process polling and profile load/save mechanisms must be prepared first

- [ ] T002 Implement dynamic health check polling timeout calculation based on `n_ctx` and model file size in `src/core/process_manager.py`
- [ ] T003 Ensure atomic load, merge, and save operations for context profiles in `src/core/config_manager.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - 고용량 컨텍스트 윈도우 동적 탐색 및 헬스체크 타임아웃 적응형 확장 (Priority: P1) 🎯 MVP

**Goal**: 소형/중형 모델의 탐색 상한선을 `max_n_ctx` (16384)로 확장하고 헬스체크 타임아웃(최대 60초)을 적용하여 4096 초과 컨텍스트 윈도우를 탐색

**Independent Test**: `uv run python scripts/benchmark_context_window.py --model qwen3.5-2b --fine-grained --json` 실행 시 `[4096, 16384]` 구간에서 5단계 이진 탐색이 수행되고 4096 초과 가용 크기가 탐색됨을 검증

### Tests for User Story 1

- [ ] T004 [P] [US1] Add unit tests for dynamic `poll_server_health` timeout scaling in `tests/unit/test_process_manager.py`
- [ ] T005 [P] [US1] Add unit tests for uncapped binary search range `[4096, 16384]` in `tests/unit/test_benchmark_context.py`

### Implementation for User Story 1

- [ ] T006 [US1] Update `scripts/benchmark_context_window.py` to uncap `model_max_rope` from `default_n_ctx` to `max_n_ctx` (default 16384) and set search iterations to 5 (`range(5)`)
- [ ] T007 [US1] Connect `poll_server_health` dynamic timeout inside `_execute_single_binary_search_inner` in `scripts/benchmark_context_window.py`
- [ ] T008 [US1] Run single model fine-grained benchmark verification scenario in `quickstart.md`

**Checkpoint**: User Story 1 is fully functional and testable independently (MVP!)

---

## Phase 4: User Story 2 - 원자적 프로필 캐시 병합 및 유실 방지 보존 메커니즘 (Priority: P2)

**Goal**: 품질 벤치마크 또는 일부 모델 벤치마크 구동 시 결과 미존재에도 `config/model_context_profiles.json`의 기존 프로필 데이터가 온전히 원자적 병합(Merge) 보존되도록 보장

**Independent Test**: `uv run python -c "from scripts.benchmark_quality import save_context_profiles_cache; save_context_profiles_cache([], {})"` 실행 후 기존 12개 프로필 캐시가 유지되는지 검증

### Tests for User Story 2

- [ ] T009 [P] [US2] Add unit tests for atomic profile cache preservation when reports list is empty in `tests/unit/test_config_manager.py`

### Implementation for User Story 2

- [ ] T010 [US2] Update `save_context_profiles_cache` in `scripts/benchmark_quality.py` to atomically load, merge, and preserve existing profiles
- [ ] T011 [US2] Update `save_benchmark_profile` in `scripts/benchmark_context_window.py` to ensure complete server config and model context profile synchronization

**Checkpoint**: User Stories 1 AND 2 work independently without data loss

---

## Phase 5: User Story 3 - 벤치마크 진단 로그 및 정밀 오류 원인 추적성 강화 (Priority: P3)

**Goal**: 이진 탐색 시도 단계별 `tested_n_ctx`, `real_vram_mb`, `status`, `reason`을 명시 기록하고 OOM/SIGKILL 예외 추적성 강화

**Independent Test**: 벤치마크 완료 후 `config/model_context_profiles.json` 파일 내 `binary_search_steps` 배열 항목의 정밀 진단 메타데이터 검증

### Tests for User Story 3

- [ ] T012 [P] [US3] Add unit tests for `binary_search_steps` step metadata output in `tests/unit/test_benchmark_context.py`

### Implementation for User Story 3

- [ ] T013 [US3] Enhance step-by-step trial logging (`tested_n_ctx`, `real_vram_mb`, `status`, `reason`) in `scripts/benchmark_context_window.py` and `logs/benchmark.log`
- [ ] T014 [US3] Add exception trapping for process termination by SIGKILL/Exit Code 137 in `scripts/benchmark_context_window.py`

**Checkpoint**: All user stories functional with full diagnostic observability

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Full regression testing and end-to-end quickstart validation

- [ ] T015 Run full Python test suite via `uv run pytest` to ensure 100% Green Pass
- [ ] T016 Execute end-to-end `quickstart.md` validation scenarios and confirm contract compliance

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Phase 6)**: Depends on all user stories completion

### Parallel Opportunities

- T004, T005 [US1 tests] can run in parallel
- T009 [US2 test] can run in parallel
- T012 [US3 test] can run in parallel
