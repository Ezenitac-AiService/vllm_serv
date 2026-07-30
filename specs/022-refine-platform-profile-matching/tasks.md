# Tasks: 플랫폼 프로필 매칭 정교화 및 출력 메시지 다듬기

**Input**: Design documents from `/specs/022-refine-platform-profile-matching/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli_contracts.md, quickstart.md

**Tests**: Tests are MANDATORY per constitution (II. 테스트 필수 원칙) - written and verified using `uv run pytest`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [x] [TaskID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project structure validation and test environment readiness

- [x] T001 Verify project structure and spec alignment in `specs/022-refine-platform-profile-matching/plan.md`
- [x] T002 Verify current pytest suite execution using `uv run pytest tests/unit/test_cpu_detector.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Update `config/platform_profiles.json` schema and entity definitions required before logic changes

- [x] T003 Update `TargetPlatformProfile` Pydantic model in `src/core/cpu_detector.py` to include `expected_avx2` attribute
- [x] T004 Add `pascal-avx2-gtx1080ti` profile to `config/platform_profiles.json` for Haswell Xeon E3-1231 v3 + GTX 1080 Ti hardware

---

## Phase 3: User Story 1 - CMake 빌드 인자 띄어쓰기 서식 버그 수정 (Priority: P1) 🎯 MVP

**Goal**: `get_llama_build_flags()`에서 생성하는 CMake 인자 문자열의 `-DGGML_F16C=ON -DGGML_FMA=ON` 공백 누락 버그 수정

**Independent Test**: `uv run python -m src.core.cpu_detector --format cmake` 실행 시 반환된 문자열에서 인자 간 공백 구분이 정확히 존재함 확인

### Tests for User Story 1

- [x] T005 [P] [US1] Write unit test for CMake build flags string spacing format in `tests/unit/test_cpu_detector.py`

### Implementation for User Story 1

- [x] T006 [US1] Fix CMake arguments formatting string in `src/core/cpu_detector.py` to ensure single-space separation between all options
- [x] T007 [US1] Verify CMake output format via `uv run pytest tests/unit/test_cpu_detector.py -k test_build_flags`

---

## Phase 4: User Story 2 - 하드웨어 프로필 매칭 로직 정교화 (Priority: P1)

**Goal**: GPU Compute Capability와 CPU AVX/AVX2 지원 여부를 복합 평가하여 Xeon E3-1231 v3 시스템에 `pascal-avx2-gtx1080ti` 프로필 매칭

**Independent Test**: Xeon E3-1231 v3 + GTX 1080 Ti 환경에서 `uv run python -m src.core.cpu_detector --match-profile` 실행 시 `pascal-avx2-gtx1080ti` 반환 확인

### Tests for User Story 2

- [x] T008 [P] [US2] Write unit tests for composite profile matching (AVX2 + Compute Cap) in `tests/unit/test_cpu_detector.py`

### Implementation for User Story 2

- [x] T009 [US2] Update `match_platform_profile()` in `src/core/cpu_detector.py` to evaluate both `compute_capability` and `supports_avx2`
- [x] T010 [US2] Verify profile matching behavior via `uv run pytest tests/unit/test_cpu_detector.py -k test_match_platform_profile`

---

## Phase 5: User Story 3 - 쉘 스크립트 출력 문구 및 안내 메시지 다듬기 (Priority: P2)

**Goal**: `make_seed_pack.sh`, `status_server.sh`, `setup.sh`의 안내 및 예시 문구를 범용 하드웨어 표현으로 정돈

**Independent Test**: `./make_seed_pack.sh` 및 `./status_server.sh` 실행 시 안내문구가 명료하고 정돈되어 출력되는지 확인

### Tests for User Story 3

- [x] T011 [P] [US3] Update shell script unit test assertions in `tests/unit/test_shell_scripts.py`

### Implementation for User Story 3

- [x] T012 [P] [US3] Polish migration guide target server text in `scripts/make_seed_pack.sh` and root `make_seed_pack.sh`
- [x] T013 [P] [US3] Polish hardware detection report header and text in `scripts/status_server.sh` and root `status_server.sh`
- [x] T014 [US3] Polish setup logs and generator template strings in `setup.sh`

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Full regression testing across the test suite and documentation verification

- [x] T015 Verify `specs/022-refine-platform-profile-matching/quickstart.md` execution scenarios
- [x] T016 Run full test suite with `uv run pytest tests/` to confirm zero regressions across all 127+ tests

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS User Stories
- **User Stories (Phase 3+)**:
  - US1 (P1) and US2 (P1) can run in parallel after Phase 2
  - US3 (P2) can run after Phase 2
- **Polish (Phase 6)**: Depends on all User Stories complete

---

## Implementation Strategy

### MVP First (User Story 1 & 2)

1. Complete Phase 1 (Setup) & Phase 2 (Foundational: Pydantic model + `platform_profiles.json`)
2. Complete Phase 3 (US1: CMake space fix) & Phase 4 (US2: Profile matching refinement)
3. Validate CLI output using `quickstart.md`
4. Complete Phase 5 (US3: Script message polish) and run full pytest suite
