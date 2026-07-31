---

description: "Task list for Seed Pack Wheel Validation & Setup Failure Diagnostics implementation"
---

# Tasks: Seed Pack Wheel Validation & Setup Failure Diagnostics (시드 팩 사전 빌드 휠 정밀 검증 기반 재빌드 및 Fast-Track 진단 강화)

**Input**: Design documents from `/specs/035-seed-pack-wheel-diagnostics/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included for each user story and must be executed using `uv run pytest`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- File paths are explicitly included in descriptions

## Path Conventions

- **Single project**: `scripts/`, `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Infrastructure setup for the pure-python binary scanner tool

- [x] T001 Create pure-python binary scanner script shell `scripts/verify_wheel_binary.py`
- [x] T002 [P] Create unit test file `tests/unit/test_wheel_scanner.py` with mock wheel test fixtures

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core ELF decoding and AVX opcode detection logic required for wheel validation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 [P] Implement ZIP `.so` entry parsing and byte opcode scanning helper in `scripts/verify_wheel_binary.py`
- [x] T004 Add CLI argument parsing and exit codes (0=valid, 1=invalid) to `scripts/verify_wheel_binary.py`

**Checkpoint**: Foundation ready - pure-python binary scanner tool functional.

---

## Phase 3: User Story 1 - 기존 사전 빌드 휠 파이썬 내장 스캐너 정밀 검증 및 조건부 재컴파일 (Priority: P1) 🎯 MVP

**Goal**: Integrate pure-python binary scanner with `make_seed_pack.sh` to validate existing wheels. Reuse valid wheels (0 AVX instrs) in 0s, delete and rebuild contaminated wheels with `-DGGML_AVX=OFF -DCMAKE_CUDA_ARCHITECTURES=61`.

**Independent Test**: `python3 scripts/verify_wheel_binary.py wheels/legacy_i7_930/*.whl` & `./scripts/make_seed_pack.sh`

### Tests for User Story 1

- [x] T005 [P] [US1] Write unit test verifying `verify_wheel_binary.py` correctly detects valid vs AVX-contaminated wheels in `tests/unit/test_wheel_scanner.py`
- [x] T006 [P] [US1] Write unit tests in `tests/unit/test_seed_pack_legacy.py` for conditional wheel validation in `make_seed_pack.sh`

### Implementation for User Story 1

- [x] T007 [US1] Update `scripts/make_seed_pack.sh` to run `scripts/verify_wheel_binary.py` against existing legacy wheels instead of checking file existence
- [x] T008 [US1] Update `scripts/make_seed_pack.sh` to clean/delete invalid wheels and force re-compile with `-DGGML_AVX=OFF -DCMAKE_CUDA_ARCHITECTURES=61`

**Checkpoint**: At this point, User Story 1 is fully functional and testable independently (MVP ready).

---

## Phase 4: User Story 2 - `setup.sh` 사전 빌드 휠 검증 실패 원인 진단 및 에러 가독성 표출 (Priority: P2)

**Goal**: Remove `2>/dev/null` error suppression in `scripts/setup.sh` during fast-track wheel validation, outputting 1-line structured failure cause and full stderr traceback.

**Independent Test**: `uv run pytest tests/unit/test_shell_scripts.py -k test_setup_diagnostics`

### Tests for User Story 2

- [x] T009 [P] [US2] Write unit test asserting `setup.sh` captures and logs stderr on wheel validation failure in `tests/unit/test_shell_scripts.py`

### Implementation for User Story 2

- [x] T010 [US2] Update `scripts/setup.sh` to capture python stderr during `llama_supports_gpu_offload()` check, format 1-line failure cause (`SIGILL`, `CUDA Error`, `ImportError`), and print traceback before fallback

**Checkpoint**: User Story 2 adds transparent failure diagnostics to `setup.sh`.

---

## Phase 5: User Story 3 - 휠 정밀 검증 및 진단 출력 회귀 테스트 수록 (Priority: P3)

**Goal**: Complete regression test suite for wheel binary scanning, conditional rebuild, and setup failure logging.

**Independent Test**: `uv run pytest tests/unit/test_seed_pack_legacy.py tests/unit/test_shell_scripts.py tests/unit/test_wheel_scanner.py`

### Tests for User Story 3

- [x] T011 [P] [US3] Add unit tests for corrupted wheel zip and edge cases in `tests/unit/test_wheel_scanner.py`
- [x] T012 [US3] Update `tests/unit/test_seed_pack_legacy.py` to assert CMAKE AVX disabling flags in `make_seed_pack.sh`

**Checkpoint**: All user stories (P1, P2, P3) complete with full test coverage.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and end-to-end suite validation

- [x] T013 [P] Update validation scenarios in `specs/035-seed-pack-wheel-diagnostics/quickstart.md`
- [x] T014 Run full test suite using `uv run pytest` to ensure zero regressions across existing codebase

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1) → User Story 2 (P2) → User Story 3 (P3)
- **Polish (Phase 6)**: Depends on all user stories being complete

### Parallel Opportunities

- T002 [P] can run in parallel with T001
- T003 [P] can run in parallel
- T005 [P] [US1] and T006 [P] [US1] can run in parallel
- T009 [P] [US2] can run in parallel
- T011 [P] [US3] can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001, T002)
2. Complete Phase 2: Foundational (T003, T004)
3. Complete Phase 3: User Story 1 (T005 - T008)
4. **STOP and VALIDATE**: Run `python3 scripts/verify_wheel_binary.py wheels/legacy_i7_930/*.whl`
5. MVP Verified!

### Incremental Delivery

1. Setup + Foundational → Pure-python binary scanner tool ready
2. Add User Story 1 (P1) → Conditional wheel validation & rebuild in `make_seed_pack.sh` (MVP!)
3. Add User Story 2 (P2) → Transparent error diagnostics in `setup.sh`
4. Add User Story 3 (P3) → Full regression test suite
5. Polish & full validation (`uv run pytest`)

---

## Phase 7: Convergence

**Purpose**: Resolve gaps identified by convergence analysis against spec, plan, and constitution.

- [x] T015 Remove `scan_so_with_objdump()` function, `subprocess`/`shutil` imports, and `has_objdump` branching from `scripts/verify_wheel_binary.py` to use only `scan_so_with_python_bytes()` per SC-002 (partial)
- [x] T016 [P] Add 035-feature diagnostic logging tests (`test_setup_sh_fast_track_diagnostic_output`, `test_setup_sh_failure_categories`) to `tests/unit/test_shell_scripts.py` per FR-003 / plan.md (partial)
- [x] T017 Run full test suite using `uv run pytest` to verify convergence fixes cause zero regressions


