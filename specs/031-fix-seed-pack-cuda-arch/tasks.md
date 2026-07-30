# Tasks: i7-930/GTX 1070 타겟 시드 팩 사전 빌드 휠 CMAKE_CUDA_ARCHITECTURES 명시 및 고속 복원 검증 통과 (031-fix-seed-pack-cuda-arch)

**Input**: Design documents from `/specs/031-fix-seed-pack-cuda-arch/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and legacy wheel storage verification

- [x] T001 Verify legacy wheel storage directory and existing test file setup in `wheels/legacy_i7_930/` and `tests/unit/test_seed_pack_legacy.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Base script permission and environment check scaffolding

- [x] T002 [P] Verify `scripts/make_seed_pack.sh` execution permissions and CLI parameters

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - i7-930 및 GTX 1070 전용 CUDA 아키텍처 사전 빌드 휠 생성 및 100% Fast-Track 복원 통과 (Priority: P1) 🎯 MVP

**Goal**: `scripts/make_seed_pack.sh`에서 `legacy-i7-930` 휠 빌드 시 `FORCE_CMAKE=1`, `CFLAGS="-march=x86-64"`, `CMAKE_ARGS="-DGGML_CUDA=ON -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_F16C=OFF -DGGML_FMA=OFF -DGGML_NATIVE=OFF -DCMAKE_CUDA_ARCHITECTURES=61"` 플래그를 추가하여 GTX 1070 GPU 타겟 휠 바이너리를 생성하고 호스트 CPU 명령어 누출(`-march=native`)을 방지

**Independent Test**: `make_seed_pack.sh` 실행 시 생성되는 휠 사전 빌드 명령 환경변수 및 CMAKE 인자를 검증하고, `setup.sh` 구동 시 소스 컴파일 Fallback 경고 없이 Fast-Track 검증이 100% 통과함을 확인

### Tests for User Story 1 (MANDATORY)

- [x] T003 [P] [US1] Write unit test for `scripts/make_seed_pack.sh` CMAKE CUDA architecture and native flags in `tests/unit/test_seed_pack_legacy.py`

### Implementation for User Story 1

- [x] T004 [US1] Update `scripts/make_seed_pack.sh` i7-930 prebuilt wheel compilation line to include `FORCE_CMAKE=1 CFLAGS="-march=x86-64" CMAKE_ARGS="-DGGML_CUDA=ON -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_F16C=OFF -DGGML_FMA=OFF -DGGML_NATIVE=OFF -DCMAKE_CUDA_ARCHITECTURES=61"`
- [x] T005 [US1] Run unit tests `tests/unit/test_seed_pack_legacy.py` for US1 to verify CMAKE flags in `scripts/make_seed_pack.sh`

**Checkpoint**: User Story 1 (MVP) complete and testable independently

---

## Phase 4: User Story 2 - 시드 팩 빌드 스크립트 CMAKE 인자 검증 단위 테스트 추가 (Priority: P2)

**Goal**: `tests/unit/test_seed_pack_legacy.py`에 `make_seed_pack.sh` CMAKE_CUDA_ARCHITECTURES 및 GGML_NATIVE 인자 포함 여부를 검증하는 단위 테스트 수트 수록 및 회귀 방지

**Independent Test**: `pytest tests/unit/test_seed_pack_legacy.py` 구동 시 모든 CMAKE 인자 검증 및 시드 팩 포장 테스트 100% 통과

### Tests for User Story 2 (MANDATORY)

- [x] T006 [P] [US2] Write test verifying `make_seed_pack.sh` wheel output directory generation and legacy prebuilt packaging assertions in `tests/unit/test_seed_pack_legacy.py`

### Implementation for User Story 2

- [x] T007 [US2] Run pytest unit test suite `tests/unit/test_seed_pack_legacy.py` to verify all legacy seed pack and setup assertion tests pass cleanly

**Checkpoint**: User Stories 1 AND 2 functional and verified

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Overall validation, Quickstart guide execution, and regression testing

- [x] T008 [P] Run full `uv run pytest` test suite to verify 0 regressions across all unit/integration tests
- [x] T009 Run quickstart validation guide in `specs/031-fix-seed-pack-cuda-arch/quickstart.md` to verify seed pack generation and fast-track setup

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
- **User Story 2 (P2)**: Builds upon US1 CMAKE args implementation to enforce regression prevention tests

### Parallel Opportunities

- T002 (Foundational script permission check) can run in parallel with T001
- T003 [US1] test can be written in parallel
- T006 [US2] test can be written in parallel
- T008 [Polish] pytest run can be executed in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Complete Phase 1 & Phase 2 (T001, T002)
2. Complete Phase 3 (T003 - T005)
3. Validate User Story 1 independently (`make_seed_pack.sh` CMAKE_CUDA_ARCHITECTURES=61 인자 및 GGML_NATIVE=OFF 지정)

### Incremental Delivery
1. Deliver US1 (GTX 1070 sm_61 타겟 휠 사전 빌드 CMAKE 인자 지정)
2. Deliver US2 (시드 팩 빌드 스크립트 CMAKE 인자 자동 검증 수트)
3. Perform Phase 5 Polish & Quickstart Validation
