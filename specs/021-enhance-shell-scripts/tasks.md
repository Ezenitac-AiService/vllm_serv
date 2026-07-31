# Tasks: 운영 쉘 스크립트 멀티 플랫폼 고도화

**Input**: Design documents from `/specs/021-enhance-shell-scripts/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli_contracts.md, quickstart.md

**Tests**: Tests are MANDATORY per constitution (II. 테스트 필수 원칙) - written and verified using `uv run pytest`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [x] [TaskID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project structure validation and test environment readiness

- [x] T001 Verify project structure and spec alignment in `specs/021-enhance-shell-scripts/plan.md`
- [x] T002 Ensure `config/platform_profiles.json` is accessible and parsed by `src/core/config_manager.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core Python CLI options (`--match-profile` & `--check-preflight`) that MUST be complete before shell script integrations

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Implement `match_platform_profile()` and `--match-profile` CLI option in `src/core/cpu_detector.py`
- [x] T004 Implement `check_hardware_preflight()` and `--check-preflight` CLI option in `src/core/cpu_detector.py`
- [x] T005 Write unit tests for `--match-profile` and `--check-preflight` CLI flags in `tests/unit/test_cpu_detector.py`

**Checkpoint**: Foundation ready - Python CLI enhancements verified by `uv run pytest tests/unit/test_cpu_detector.py`

---

## Phase 3: User Story 1 - status_server.sh 하드웨어 리포트 고도화 (Priority: P1) 🎯 MVP

**Goal**: `./status_server.sh` 실행 시 CPU 모델/SIMD 지원 현황, GPU Compute Capability, 매칭된 플랫폼 프로필 정보를 실시간 리포트로 표시

**Independent Test**: `./status_server.sh` 실행 결과에 CPU SIMD, GPU CC (`sm_61`, `sm_86` 등), 매칭 프로필명이 명확히 출력되는지 확인

### Tests for User Story 1

- [x] T006 [P] [US1] Create unit tests for `status_server.sh` report output formatting in `tests/unit/test_shell_scripts.py`

### Implementation for User Story 1

- [x] T007 [US1] Update `scripts/status_server.sh` to invoke `uv run python -m src.core.cpu_detector --report` and display profile match details
- [x] T008 [US1] Verify `status_server.sh` output format and responsiveness (<5초) on host environment

**Checkpoint**: User Story 1 fully functional and independently testable via `./status_server.sh`

---

## Phase 4: User Story 2 - start_server.sh 사전 점검 및 Fail-Fast 고도화 (Priority: P1)

**Goal**: `./start_server.sh` 백그라운드 전환 전 하드웨어 사전 점검(Pre-flight check) 수행 및 GPU/CUDA 감지 실패 시 해결 조치 안내문과 함께 exit 1로 조기 종료

**Independent Test**: GPU가 없거나 NVCC 미설치 상태에서 `./start_server.sh` 실행 시 데몬 생성 없이 에러 안내문 출력 후 exit 1 종료 확인

### Tests for User Story 2

- [x] T009 [P] [US2] Create unit tests for `start_server.sh` pre-flight check pass/fail behavior in `tests/unit/test_shell_scripts.py`

### Implementation for User Story 2

- [x] T010 [US2] Update `scripts/start_server.sh` to integrate `--check-preflight` before daemonizing and print detailed troubleshooting guide on failure
- [x] T011 [US2] Add integration test for server start pre-flight validation in `tests/integration/test_build_pipeline.py`

**Checkpoint**: User Story 2 pre-flight check independently testable via `./scripts/start_server.sh`

---

## Phase 5: User Story 3 - setup.sh 플랫폼 인지 & CMAKE_ARGS 강화 (Priority: P2)

**Goal**: `./setup.sh` 실행 시 감지된 하드웨어를 `config/platform_profiles.json` 프로필과 대조하여 일치 프로필 안내 및 동적 CMAKE_ARGS 적용 로그 표시

**Independent Test**: `./setup.sh` 실행 시 CPU/GPU 감지 리포트 및 매칭 프로필명이 명확히 표시되는지 확인

### Tests for User Story 3

- [x] T012 [P] [US3] Create unit tests for `setup.sh` profile display and CMAKE_ARGS propagation in `tests/unit/test_shell_scripts.py`

### Implementation for User Story 3

- [x] T013 [US3] Update `setup.sh` to invoke `cpu_detector --match-profile` and report target platform profile match during setup
- [x] T014 [US3] Verify `setup.sh` build flag logs and platform detection in `tests/integration/test_build_pipeline.py`

**Checkpoint**: User Story 3 platform-aware setup functional and testable

---

## Phase 6: User Story 4 - make_seed_pack.sh 멀티 플랫폼 아카이빙 (Priority: P3)

**Goal**: `./scripts/make_seed_pack.sh` 실행 시 `config/platform_profiles.json` 파일 수록을 보장하고 타겟 플랫폼 이관 안내문 출력

**Independent Test**: 아카이브 생성 후 파일 목록에 `config/platform_profiles.json`이 존재함을 확인

### Tests for User Story 4

- [x] T015 [P] [US4] Create unit test verifying `make_seed_pack.sh` includes `config/platform_profiles.json` in `tests/unit/test_shell_scripts.py`

### Implementation for User Story 4

- [x] T016 [US4] Update `scripts/make_seed_pack.sh` to package `config/platform_profiles.json` and print multi-platform migration guide
- [x] T017 [US4] Verify archive size (<10MB) and contents after running `./scripts/make_seed_pack.sh`

**Checkpoint**: User Story 4 seed pack packaging and migration guide functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Multi-script integration verification, documentation validation, and backward compatibility

- [x] T018 [P] Verify backward compatibility of `scripts/stop_server.sh` and daemon lifecycle
- [x] T019 Update `specs/021-enhance-shell-scripts/quickstart.md` if any CLI flags updated
- [x] T020 Run full test suite with `uv run pytest tests/` to confirm zero regressions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all User Stories
- **User Stories (Phase 3+)**: All depend on Foundational (Phase 2) completion
  - US1 (P1) and US2 (P1) can run in parallel after Phase 2
  - US3 (P2) can run after Phase 2
  - US4 (P3) can run after Phase 2
- **Polish (Phase 7)**: Depends on all User Stories being complete

### Parallel Opportunities

- T006 [P], T009 [P], T012 [P], T015 [P] (unit test creations in `test_shell_scripts.py`) can run in parallel
- After Phase 2 completes, US1 (`status_server.sh`), US2 (`start_server.sh`), US3 (`setup.sh`), and US4 (`make_seed_pack.sh`) can be implemented in parallel as they touch separate script files.

---

## Implementation Strategy

### MVP First (User Story 1 & 2)

1. Complete Phase 1 (Setup) & Phase 2 (Foundational: `--match-profile` & `--check-preflight`)
2. Complete Phase 3 (US1: `status_server.sh`) & Phase 4 (US2: `start_server.sh`)
3. **STOP and VALIDATE**: Verify server status report & pre-flight check on host
4. Continue with US3 & US4 incrementally
