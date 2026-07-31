# Tasks: 구형 i7-930 플랫폼 전용 사전 컴파일 라이브러리 시드 팩(Seed Pack) 번들링 및 고속 구축 (029-prebuild-legacy-seed-pack)

**Input**: Design documents from `/specs/029-prebuild-legacy-seed-pack/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and legacy wheel storage directory structure

- [x] T001 Create directory structure for legacy wheels in `wheels/legacy_i7_930/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Base test framework scaffolding for shell script validation

- [x] T002 [P] Create test suite file `tests/unit/test_seed_pack_legacy.py` for testing seed pack wheel build and setup fast-track logic

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - 구형 i7-930 장비 시드 팩 기반 C++ 컴파일 생략 및 Instant 구축 (Priority: P1) 🎯 MVP

**Goal**: i7-930(Nehalem) 환경에서 긴 소스 컴파일 없이 사전 컴파일 휠(`.whl`)을 `uv pip install`로 3초 내 주입하여 구축 시간 3분 이내 달성

**Independent Test**: i7-930 모의/실 하드웨어 감지 환경에서 `scripts/setup.sh` 실행 시 C++ 재컴파일 없이 `wheels/legacy_i7_930/*.whl`이 주입되고 GPU 가속 테스트가 통과함을 검증

### Tests for User Story 1 (MANDATORY)

- [x] T003 [P] [US1] Write test for `scripts/make_seed_pack.sh` i7-930 prebuilt wheel packaging in `tests/unit/test_seed_pack_legacy.py`
- [x] T004 [P] [US1] Write test for `scripts/setup.sh` i7-930 fast-track wheel installation in `tests/unit/test_seed_pack_legacy.py`

### Implementation for User Story 1

- [x] T005 [US1] Update `scripts/make_seed_pack.sh` to pre-compile i7-930 `.whl` with `CFLAGS="-march=x86-64"` and `CMAKE_ARGS="-DGGML_CUDA=ON -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_F16C=OFF -DGGML_FMA=OFF"` into `wheels/legacy_i7_930/`, ensuring `wheels/` is explicitly included in tar/zip packaging (overriding tar exclusions) and verified in archive
- [x] T006 [US1] Update `scripts/setup.sh` to detect `legacy-i7-930-gtx1070` platform (with Nehalem AVX-missing fallback protection) and execute `uv pip install` fast-track wheel injection from `wheels/legacy_i7_930/*.whl`
- [x] T007 [US1] Run unit tests `tests/unit/test_seed_pack_legacy.py` for US1 to verify fast-track wheel installation and GPU offload assertion

**Checkpoint**: User Story 1 (MVP) complete and testable independently

---

## Phase 4: User Story 2 - 현대적 CPU 플랫폼(Platform A/B) 호환성 & Fallback 유지 (Priority: P2)

**Goal**: i7-930 휠 유실 시 소스 컴파일 Fallback 보장 및 Platform A/B(Xeon E3 / Core i7-4770) 장비의 AVX2 동적 컴파일 최적화 유지

**Independent Test**: Platform A/B 프로필 환경 및 휠 유실 시 소스 컴파일 Fallback 경고 로그 출력 및 정상 설치 검증

### Tests for User Story 2 (MANDATORY)

- [x] T008 [P] [US2] Write test for missing wheel fallback on i7-930 and Platform A/B AVX2 compilation preservation in `tests/unit/test_seed_pack_legacy.py`

### Implementation for User Story 2

- [x] T009 [US2] Add fallback warning log and source compilation fallback in `scripts/setup.sh` when `wheels/legacy_i7_930/*.whl` is missing or invalid
- [x] T010 [US2] Verify Platform A/B profiles retain native AVX/AVX2 CMAKE compilation in `scripts/setup.sh` and execute test suite

**Checkpoint**: User Stories 1 AND 2 functional and verified

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Overall validation, Quickstart guide execution, and regression testing

- [x] T011 [P] Run full `uv run pytest` test suite to verify 0 regressions across all unit/integration tests
- [x] T012 Run quickstart validation guide in `specs/029-prebuild-legacy-seed-pack/quickstart.md` to verify seed pack generation and fast-track setup

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
- **User Story 2 (P2)**: Builds upon US1 wheel detection logic to add fallback and Platform A/B isolation

### Parallel Opportunities

- T002 (Foundational test scaffolding) can be created in parallel with T001
- T003 [US1] and T004 [US1] tests can be written in parallel
- T008 [US2] test can be written in parallel
- T011 [Polish] pytest run can be executed in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Complete Phase 1 & Phase 2 (T001, T002)
2. Complete Phase 3 (T003 - T007)
3. Validate User Story 1 independently (<3분 구축 및 휠 주입 검증)

### Incremental Delivery
1. Deliver US1 (i7-930 Fast-Track 시드 팩)
2. Deliver US2 (Fallback 및 Platform A/B 격리 보장)
3. Perform Phase 5 Polish & Quickstart Validation
