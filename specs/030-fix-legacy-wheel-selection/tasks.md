# Tasks: 구형 i7-930 타겟 패키지 설치 시 llama_cpp_python 사전 빌드 휠 정확한 선택 및 복원 오류 수정 (030-fix-legacy-wheel-selection)

**Input**: Design documents from `/specs/030-fix-legacy-wheel-selection/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and legacy wheel storage verification

- [x] T001 Verify directory structure for legacy wheels in `wheels/legacy_i7_930/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Base test framework scaffolding for shell script validation

- [x] T002 [P] Create test suite file `tests/unit/test_seed_pack_legacy.py` for testing seed pack wheel build and setup fast-track logic

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - 구형 i7-930 타겟 플랫폼의 llama_cpp_python 사전 컴파일 휠 명시적 탐색 및 고속 설치 (Priority: P1) 🎯 MVP

**Goal**: `wheels/legacy_i7_930/` 내 다종 휠 공존 시 `head -n 1` 오탐을 제거하고 `ls -v wheels/legacy_i7_930/llama_cpp_python*.whl 2>/dev/null | tail -n 1` 패턴으로 `llama_cpp_python` 휠을 명시적 선택하여 `--no-index --find-links` 오프라인 고속 주입 복원

**Independent Test**: `wheels/legacy_i7_930/` 디렉터리에 `annotated_doc-*.whl`과 `llama_cpp_python-*.whl`이 공존할 때 `scripts/setup.sh` 실행 시 `llama_cpp_python` 사전 빌드 휠이 정확히 정밀 매칭/설치되고 GPU 오프로드 검증이 통과함을 검증

### Tests for User Story 1 (MANDATORY)

- [x] T003 [P] [US1] Write test for `scripts/setup.sh` explicit `llama_cpp_python*.whl` matching and `--no-index --find-links` offline installation in `tests/unit/test_seed_pack_legacy.py`

### Implementation for User Story 1

- [x] T004 [US1] Update `scripts/setup.sh` to match `llama_cpp_python*.whl` via `ls -v wheels/legacy_i7_930/llama_cpp_python*.whl 2>/dev/null | tail -n 1` and execute `uv pip install "$LEGACY_WHEEL" --force-reinstall --no-index --find-links wheels/legacy_i7_930`
- [x] T005 [US1] Run unit tests `tests/unit/test_seed_pack_legacy.py` for US1 to verify wheel matching and GPU offload assertion

**Checkpoint**: User Story 1 (MVP) complete and testable independently

---

## Phase 4: User Story 2 - llama_cpp_python 사전 빌드 휠 부재 또는 검증 실패 시 안정적 소스 컴파일 Fallback (Priority: P2)

**Goal**: `llama_cpp_python` 사전 빌드 휠 부재 또는 복원 후 GPU 오프로드 검증(`llama_supports_gpu_offload()`) 실패 시 에러 종료 없이 소스 컴파일 파이프라인으로 안전 Fallback

**Independent Test**: `wheels/legacy_i7_930/` 내 `llama_cpp_python` 휠이 없거나 휠 복원 후 GPU 오프로드 검증 실패 시 Fallback 경고 로그 출력 후 `CMAKE_ARGS` 소스 컴파일 파이프라인으로 전환됨을 검증

### Tests for User Story 2 (MANDATORY)

- [x] T006 [P] [US2] Write test for missing wheel and GPU offload check failure fallback in `tests/unit/test_seed_pack_legacy.py`

### Implementation for User Story 2

- [x] T007 [US2] Update `scripts/setup.sh` to catch GPU offload assertion failure or missing wheel and fallback gracefully to `INSTALLED_VIA_FAST_TRACK=0` C++ source compilation
- [x] T008 [US2] Run unit tests `tests/unit/test_seed_pack_legacy.py` to verify US2 fallback behavior

**Checkpoint**: User Stories 1 AND 2 functional and verified

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Overall validation, Quickstart guide execution, and regression testing

- [x] T009 [P] Run full `uv run pytest` test suite to verify 0 regressions across all unit/integration tests
- [x] T010 Run quickstart validation guide in `specs/030-fix-legacy-wheel-selection/quickstart.md` to verify seed pack generation and fast-track setup

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS User Stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) completion (MVP)
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2) and US1 completion
- **Polish (Phase 5)**: Depends on User Stories 1 and 2 completion

### User Story Dependencies

- **User Story 1 (P1)**: Independent MVP story
- **User Story 2 (P2)**: Builds upon US1 wheel detection logic to add fallback and error resilience

### Parallel Opportunities

- T002 (Foundational test scaffolding) can be created in parallel with T001
- T003 [US1] test can be written in parallel
- T006 [US2] test can be written in parallel
- T009 [Polish] pytest run can be executed in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Complete Phase 1 & Phase 2 (T001, T002)
2. Complete Phase 3 (T003 - T005)
3. Validate User Story 1 independently (<5s Fast-Track 휠 주입 및 오프라인 복원 검증)

### Incremental Delivery
1. Deliver US1 (llama_cpp_python 휠 정밀 매칭 및 오프라인 복원)
2. Deliver US2 (검증 실패 시 자동 소스 컴파일 Fallback)
3. Perform Phase 5 Polish & Quickstart Validation
