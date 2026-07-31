# Tasks: 시드팩(Seed Pack) 패키징 시 명세서(specs/) 및 샘플 파일(samples/) 수록 포함 개선

**Input**: Design documents from `/specs/065-seed-pack-specs-samples/`

**Prerequisites**: [plan.md](file:///home/dev/storage/vllm_serv/specs/065-seed-pack-specs-samples/plan.md), [spec.md](file:///home/dev/storage/vllm_serv/specs/065-seed-pack-specs-samples/spec.md), [research.md](file:///home/dev/storage/vllm_serv/specs/065-seed-pack-specs-samples/research.md), [data-model.md](file:///home/dev/storage/vllm_serv/specs/065-seed-pack-specs-samples/data-model.md), [quickstart.md](file:///home/dev/storage/vllm_serv/specs/065-seed-pack-specs-samples/quickstart.md)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and Seed Pack script environment verification

- [x] T001 Verify `scripts/make_seed_pack.sh` execution and target directory structures (`specs/`, `samples/`, `.legacy/`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Update tar and zip exclusion rules in `scripts/make_seed_pack.sh`

- [x] T002 Remove `--exclude="specs"` and `--exclude=".legacy"` flags from tar and zip packaging commands in `scripts/make_seed_pack.sh`

**Checkpoint**: Foundation ready - user story implementation can begin in parallel

---

## Phase 3: User Story 1 - Seed Pack 생성 시 `specs/`, `samples/`, `.legacy/` 수록 (`scripts/make_seed_pack.sh`) (Priority: P1) 🎯 MVP

**Goal**: Ensure `make_seed_pack.sh` bundles `specs/`, `samples/`, and `.legacy/` into `dist/vllm_serv_seed.tar.gz` and verifies their presence post-build.

**Independent Test**: Run `./make_seed_pack.sh` and verify archive contents contains `samples/common.py` and `specs/`.

### Implementation for User Story 1

- [x] T003 [US1] Add Post-Build archive verification assertions for `samples/common.py` and `specs/` in `scripts/make_seed_pack.sh`
- [x] T004 [P] [US1] Test manual execution of `./make_seed_pack.sh` and verify `dist/vllm_serv_seed.tar.gz` size (< 15MB) and contents

**Checkpoint**: User Story 1 fully functional — Seed Pack includes specs, samples, and legacy modules.

---

## Phase 4: User Story 2 - 시드팩 검증 수트 (`tests/unit/test_seed_pack.py`) 수록 항목 검증 보강 (Priority: P2)

**Goal**: Update unit test suite to assert that `samples/` and `specs/` are included in the generated seed pack archive.

**Independent Test**: Run `uv run pytest tests/unit/test_seed_pack.py` and verify 100% Green Pass.

### Tests for User Story 2 ⚠️

- [x] T005 [P] [US2] Update `tests/unit/test_seed_pack.py` to assert `samples/common.py` and `specs/` exist in generated archive

**Checkpoint**: User Story 2 fully functional — unit test suite asserting seed pack archive contents.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Quickstart validation and full regression test suite execution

- [x] T006 Run quickstart validation scenarios documented in `quickstart.md`
- [x] T007 Run full regression test suite (`uv run pytest`) to ensure 100% Green Pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1) → User Story 2 (P2)
- **Polish (Phase 5)**: Depends on all user stories being complete

### Parallel Opportunities

- T004, T005 can run in parallel (different files/tasks, no dependencies)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup (Phase 1) and Foundational (Phase 2)
2. Complete User Story 1 (Phase 3)
3. Validate archive packaging via `./make_seed_pack.sh`

### Incremental Delivery

1. Deliver MVP (`make_seed_pack.sh` exclusion update & post-build checks)
2. Update unit test suite in `tests/unit/test_seed_pack.py`
3. Execute full regression suite (`uv run pytest`)
