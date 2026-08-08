# Tasks: setup.sh 강제 빌드 옵션(--force-build) 추가 및 benchmark_context_window NameError 크래시 수정 (Fix setup.sh Force Build & Benchmark Crash)

**Input**: Design documents from `/specs/114-fix-setup-force-build-and-benchmark-crash/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Exact file paths included in all descriptions.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verification of task environment and feature directory structure

- [x] T001 Verify feature specification and design documents in `specs/114-fix-setup-force-build-and-benchmark-crash/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Unit test suite expansion to capture force build and NameError requirements before implementation

- [x] T002 Add unit test for benchmark_context_window remaining_kv_budget variable calculation in `tests/unit/test_benchmark_context_window.py`
- [x] T003 [P] Add unit test cases for setup.sh --force-build CLI flag and Fast-Track bypass logic in `tests/unit/test_shell_scripts.py`

**Checkpoint**: Foundational test cases ready - implementation phase can now begin.

---

## Phase 3: User Story 1 - setup.sh 강제 빌드(--force-build) 및 --wheel-path 재설치 강제화 (Priority: P1) 🎯 MVP

**Goal**: `--force-build` CLI 플래그 추가 및 `--wheel-path` 사용 시 기존 캐시 오판을 강제 우회하여 CUDA 가속 휠이 원스톱 재설치되도록 보장

**Independent Test**: `./setup.sh --force-build --skip-benchmark` 및 `./setup.sh --wheel-path <PATH> --skip-benchmark` 구동 시 Fast-Track 재사용 로그 스킵 및 CUDA 가속 활성화 검증

### Implementation for User Story 1

- [x] T004 [P] [US1] Add `--force-build` CLI option parsing and update `--help` usage output in `scripts/setup.sh`
- [x] T005 [US1] Bypass Fast-Track wheel reuse when `FORCE_BUILD=1` or `WHEEL_PATH` is specified in `scripts/setup.sh` to force `--no-cache-dir` C++ re-compilation or `--force-reinstall`

**Checkpoint**: At this point, User Story 1 (MVP) is fully functional and testable independently.

---

## Phase 4: User Story 2 - benchmark_context_window.py NameError 예외 차단 (Priority: P1) 🎯 MVP

**Goal**: `benchmark_context_window()` 함수 내부에서 `remaining_kv_budget` 미정의 상태 참조로 인한 `NameError` 크래시 근본 차단

**Independent Test**: `python scripts/benchmark_context_window.py` 실행 시 NameError 0건 및 벤치마크 정상 완수

### Implementation for User Story 2

- [x] T006 [P] [US2] Declare `usable_vram` and `remaining_kv_budget` calculation before `calculate_max_allocatable_n_ctx` call in `scripts/benchmark_context_window.py`

**Checkpoint**: User Stories 1 AND 2 are both complete and independently testable.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: End-to-end quickstart validation and full suite regression testing

- [x] T007 Run validation scenarios in `specs/114-fix-setup-force-build-and-benchmark-crash/quickstart.md`
- [x] T008 Run full unit regression test suite `uv run pytest tests/unit/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS User Story implementation.
- **User Story 1 (Phase 3)**: Depends on Foundational completion.
- **User Story 2 (Phase 4)**: Depends on Foundational completion (can run in parallel with US1).
- **Polish (Phase 5)**: Depends on US1 & US2 implementation completion.

### Parallel Opportunities

- T003 can run in parallel with T002 in Phase 2.
- T004, T006 can run in parallel in Phase 3/4.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & Phase 2 foundational tests.
2. Implement T004 & T005 (`setup.sh` --force-build & --wheel-path bypass).
3. Validate MVP test suite: `uv run pytest tests/unit/test_shell_scripts.py`.

### Incremental Delivery

1. Complete US1 -> MVP validated.
2. Complete US2 -> NameError fix validated.
3. Run Phase 5 polish & full regression test suite.
