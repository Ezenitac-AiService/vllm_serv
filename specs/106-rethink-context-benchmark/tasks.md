# Tasks: 컨텍스트 윈도우 벤치마킹 로직 전면 재검토 및 가용성 보장 (Rethink Context Benchmark Logic)

**Input**: Design documents from `/specs/106-rethink-context-benchmark/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Unit and integration tests are mandatory per Constitution Principle II (Strict Real Verification & Real-Integration TDD Discipline).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Includes exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `scripts/`, `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and prerequisite verification

- [X] T001 Verify feature branch environment and Python virtualenv dependencies in `pyproject.toml`
- [X] T002 [P] Verify PyNVML and GPU capability detection in `src/core/gpu_detector.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core helper infrastructure that MUST be complete before user stories can be implemented

- [X] T003 [P] Add real-time NVML free VRAM (`free_vram_mb`) snapshot helper in `src/core/gpu_detector.py`
- [X] T004 [P] Prepare endpoint fallback helper structure for `poll_server_health` in `src/core/process_manager.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - 실시간 GPU VRAM 및 백그라운드 서빙 서버 점유 상태 감지 (Priority: P1) 🎯 MVP

**Goal**: GPU 하드웨어 전체 용량이 아닌 실시간 NVML 가용 VRAM(`free_vram_mb`)을 반영하여 백그라운드 서버 점유 중에도 OOM 크래시 없이 안전하게 사전 검증 및 평가 수행

**Independent Test**: 백그라운드 서빙 서버(포트 8089/8090/8091)가 VRAM 4.4GB를 점유하는 상태에서 `uv run python scripts/benchmark_context_window.py --force-benchmark` 실행 시 메인 서버 사살 및 OOM 없이 안전 처리됨을 검증

### Tests for User Story 1

- [X] T005 [P] [US1] Write unit test for real-time free VRAM pre-flight calculation in `tests/unit/test_gpu_detector.py`
- [X] T006 [P] [US1] Write unit test for background server VRAM occupancy handling in `tests/unit/test_benchmark_context_window.py`

### Implementation for User Story 1

- [X] T007 [US1] Update `_execute_single_binary_search_inner` in `scripts/benchmark_context_window.py` to use `free_vram_mb` instead of static `total_vram_mb - 500`
- [X] T008 [US1] Update `evaluate_all_catalog_models` pre-flight check in `scripts/benchmark_context_window.py` to detect active server VRAM usage and display warnings

**Checkpoint**: User Story 1 complete and independently testable (MVP!)

---

## Phase 4: User Story 2 - 벤치마크 실패 시 기존 프로파일 안전 보존 및 원자적 갱신 (Priority: P2)

**Goal**: 벤치마크 중 일시적 프로세스 실패/타임아웃 발생 시 기존 정상 프로파일을 유실/더미 덮어쓰지 않고 안전 보존하며 원자적 쓰기로 프로파일 무결성 보장

**Independent Test**: 기존 정상 프로파일이 적재된 상태에서 벤치마크 실패 유도 시 기존 `max_context_length` 결과가 유실되거나 2048 fallback으로 덮어씌워지지 않음을 검증

### Tests for User Story 2

- [X] T009 [P] [US2] Write unit test for non-destructive profile preservation in `tests/unit/test_benchmark_context_window.py`

### Implementation for User Story 2

- [X] T010 [US2] Modify `_record_unsupported_fallback_profile` in `scripts/benchmark_context_window.py` to preserve existing valid profiles unless `--force-overwrite-profiles` is set
- [X] T011 [US2] Implement atomic file write (`os.replace`) for `save_model_context_profiles` in `src/core/config_manager.py`
- [X] T012 [US2] Add CLI flag `--force-overwrite-profiles` in `scripts/benchmark_context_window.py`

**Checkpoint**: User Stories 1 and 2 complete and independently testable

---

## Phase 5: User Story 3 - 서브프로세스 정리 시 타 서빙 프로세스 무차별 종료 방지 및 헬스체크 호환성 (Priority: P3)

**Goal**: 와일드카드 `pkill -9 -f llama-server` 사살을 전면 제거하고 8081 바인딩 포트/자식 PID 정밀 정리로 메인 서버(8089/8090/8091) 보호 및 `llama_cpp.server` `/v1/models` 폴백 헬스체크 적용

**Independent Test**: 메인 서버 구동 중 벤치마크 실행/종료 시 메인 서버 PID가 사살되지 않고 `llama_cpp.server` 헬스체크 폴백이 정상 작동함을 검증

### Tests for User Story 3

- [X] T013 [P] [US3] Write unit test for pinpoint process cleanup without wildcard `pkill` in `tests/unit/test_process_manager_cleanup.py`
- [X] T014 [P] [US3] Write unit test for `poll_server_health` `/v1/models` fallback logic in `tests/unit/test_process_manager_health.py`

### Implementation for User Story 3

- [X] T015 [US3] Update `force_kill_zombie_llama_servers` and cleanup hooks in `src/core/process_manager.py` to target only port 8081 socket (`fuser`) and registered child PIDs
- [X] T016 [US3] Implement `/v1/models` fallback polling on 404 in `poll_server_health` in `src/core/process_manager.py`

**Checkpoint**: All user stories implemented and testable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Goal**: End-to-end integration validation and full suite regression testing

- [X] T017 [P] Run quickstart validation guide scenarios in `specs/106-rethink-context-benchmark/quickstart.md`
- [X] T018 Run full test suite regression (`uv run pytest`) to ensure 100% test pass rate

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: Depend on Foundational phase completion
  - Sequential priority order: US1 (P1) → US2 (P2) → US3 (P3)
- **Polish (Phase 6)**: Depends on all user stories completion

### Parallel Opportunities

- T002 (Setup) can run in parallel with T001
- T003, T004 (Foundational) can run in parallel
- T005, T006 (US1 Tests) can run in parallel
- T009 (US2 Test) can run in parallel
- T013, T014 (US3 Tests) can run in parallel
- T017 (Polish Quickstart) can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & Phase 2
2. Complete Phase 3 (User Story 1)
3. Validate User Story 1 independently with `tests/unit/test_benchmark_context_window.py`

### Incremental Delivery

1. Foundation ready (Phase 1 & 2)
2. Add US1 → Real-time Free VRAM & Pre-flight check (MVP)
3. Add US2 → Non-destructive profile preservation & Atomic write
4. Add US3 → Pinpoint process cleanup & `/v1/models` health check fallback
5. Final Polish & full regression (`uv run pytest`)
