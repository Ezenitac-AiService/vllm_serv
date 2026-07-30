# Tasks: 시드 팩 호스트 독립성 및 경량화 - 기기 특정 벤치마크 캐시 및 레거시 파일 배제 (033-exclude-benchmark-cache-seed-pack)

**Input**: Design documents from `/specs/033-exclude-benchmark-cache-seed-pack/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and seed pack script inspection

- [x] T001 Verify `scripts/make_seed_pack.sh` current archive creation logic and exclusion patterns

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Base archiving pattern rules inspection

- [x] T002 [P] Verify tar/zip `--exclude` pattern rules in `scripts/make_seed_pack.sh`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - 타겟 서버 이관 시 개발 머신 벤치마크 파일 및 레거시 아티팩트 배제 보장 (Priority: P1) 🎯 MVP

**Goal**: `scripts/make_seed_pack.sh` 실행 시 `config/model_context_profiles.json`, `.legacy/`, `benchmark_results.json`, `*.jsonl` 항목을 배제 패턴에 명시 추가하여 시드 팩 호스트 독립성 및 경량화 보장

**Independent Test**: `make_seed_pack.sh` 실행 후 `dist/vllm_serv_seed.tar.gz` 아카이브 내부에 `config/model_context_profiles.json`, `.legacy/`, `benchmark_results.json` 파일이 존재하지 않음을 검증

### Tests for User Story 1 (MANDATORY)

- [x] T003 [P] [US1] Write unit test assertions for seed pack exclusion of `config/model_context_profiles.json`, `.legacy/`, and `benchmark_results.json` in `tests/unit/test_seed_pack.py`

### Implementation for User Story 1

- [x] T004 [US1] Update `scripts/make_seed_pack.sh` tar and zip `--exclude` patterns to explicitly include `config/model_context_profiles.json`, `.legacy`, `.legacy/*`, `benchmark_results.json`, and `*.jsonl`
- [x] T005 [US1] Execute `./scripts/make_seed_pack.sh` to generate seed pack and verify tarball contents exclude benchmark cache and legacy files

**Checkpoint**: User Story 1 (MVP) complete and testable independently

---

## Phase 4: User Story 2 - 시드 팩 생성 스크립트 아카이브 검증 테스트 강화 (Priority: P2)

**Goal**: `tests/unit/test_seed_pack.py`에서 tarball 및 zip 아카이브 생성 시 `config/model_context_profiles.json` 및 `.legacy/` 미포함 여부를 자동 검증하도록 테스트 수트 강화

**Independent Test**: `uv run pytest tests/unit/test_seed_pack.py` 구동 시 배제 검증 단위를 포함한 전체 테스트 100% 통과

### Tests for User Story 2 (MANDATORY)

- [x] T006 [P] [US2] Update `tests/unit/test_seed_pack.py` to verify both tarball and zip format exclusions for `config/model_context_profiles.json` and `.legacy`

### Implementation for User Story 2

- [x] T007 [US2] Run `uv run pytest tests/unit/test_seed_pack.py` to verify 100% pass for archive exclusion assertions

**Checkpoint**: User Stories 1 AND 2 functional and verified

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Overall validation, Quickstart guide execution, and regression testing

- [x] T008 [P] Run full `uv run pytest` test suite to verify 0 regressions across all unit/integration tests
- [x] T009 Run quickstart validation guide in `specs/033-exclude-benchmark-cache-seed-pack/quickstart.md`

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
- **User Story 2 (P2)**: Builds upon US1 exclusion rules to enforce unit test coverage

### Parallel Opportunities

- T002 (Foundational pattern rule check) can run in parallel with T001
- T003 [US1] test can be written in parallel
- T006 [US2] test can be written in parallel
- T008 [Polish] pytest run can be executed in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Complete Phase 1 & Phase 2 (T001, T002)
2. Complete Phase 3 (T003 - T005)
3. Validate User Story 1 independently (`make_seed_pack.sh` 실행 시 `config/model_context_profiles.json` 및 `.legacy/` 미포함 검증)

### Incremental Delivery
1. Deliver US1 (시드 팩 기기 특정 캐시 및 레거시 파일 배제)
2. Deliver US2 (시드 팩 자동 검증 단위 테스트 강화)
3. Perform Phase 5 Polish & Quickstart Validation
