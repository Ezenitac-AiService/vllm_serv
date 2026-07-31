# Tasks: 061-fix-seed-pack-exclusions-gpu-verification

**Input**: Design documents from `specs/061-fix-seed-pack-exclusions-gpu-verification/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Exact file paths included in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Workspace environment verification and context alignment

- [x] T001 Verify active feature configuration in `.specify/feature.json` and workspace clean state

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared virtualenv Python interpreter path verification for isolated subprocess calls

- [x] T002 Verify `.venv/bin/python` virtualenv interpreter availability and execution capability in `scripts/setup.sh`

---

## Phase 3: User Story 1 - 씨드 팩 아카이브 경량화 (`specs/`, `.agents/`, `.specify/` exclusion) (Priority: P1) 🎯 MVP

**Goal**: Exclude dev spec and agent tool directories from seed pack archive while retaining `tests/` for target server verification.

**Independent Test**: `./scripts/make_seed_pack.sh --skip-legacy-build` produces `dist/vllm_serv_seed.tar.gz` with zero files under `specs/`, `.agents/`, or `.specify/`, but retaining `tests/`.

### Tests for User Story 1

- [x] T003 [P] [US1] Add unit test assertions checking tarball exclusion rules (`specs`, `.agents`, `.specify` excluded, `tests` retained) in `tests/unit/test_seed_pack.py`

### Implementation for User Story 1

- [x] T004 [US1] Update `scripts/make_seed_pack.sh` tar creation with `--exclude="specs" --exclude=".agents" --exclude=".specify"` and zip creation with `-x "specs/*" -x ".agents/*" -x ".specify/*"`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - `setup.sh` Fast-Track GPU 검증 파이프라인 격리 (`.venv/bin/python` 사용) (Priority: P1)

**Goal**: Prevent `uv run` auto-sync from overwriting restored prebuilt CUDA wheels with CPU wheels during `setup.sh` GPU verification.

**Independent Test**: `./scripts/setup.sh` successfully verifies CUDA GPU offload (`llama_supports_gpu_offload() == True`) using `.venv/bin/python` without triggering `uv` auto-sync or package re-installation.

### Tests for User Story 2

- [x] T005 [P] [US2] Add unit test assertions checking `.venv/bin/python` execution in `tests/unit/test_seed_pack.py`

### Implementation for User Story 2

- [x] T006 [US2] Update `scripts/setup.sh` GPU offload verification and pre-check snippets to execute `.venv/bin/python` directly instead of `uv run python`

**Checkpoint**: User Story 1 and User Story 2 are fully integrated.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Validation and full suite regression testing

- [x] T007 [P] Execute full unit regression test suite `uv run pytest tests/unit/test_seed_pack.py`
- [x] T008 Execute end-to-end quickstart verification scenario `./scripts/make_seed_pack.sh --skip-legacy-build` and verify setup fast-track behavior

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Setup.
- **User Story 1 (Phase 3 - MVP)**: Depends on Phase 2.
- **User Story 2 (Phase 4)**: Depends on Phase 3.
- **Polish (Phase 5)**: Depends on Phase 4.

### Parallel Opportunities

- T003 [P] and T005 [P] can run in parallel with foundational preparation.
- T007 [P] can run in parallel during final verification.
