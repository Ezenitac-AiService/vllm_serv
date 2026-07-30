# Tasks: Seed Pack Archiver & Migration Pipeline

**Input**: Design documents from `/specs/019-seed-pack-generator/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (`[US1]`, `[US2]`, `[US3]`)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initial script scaffolding and directory setup

- [x] T001 Create output directory `dist/` and working directory normalization in `scripts/make_seed_pack.sh`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: POSIX tool availability check and CLI option parsing framework

**⚠️ CRITICAL**: No user story implementation can begin until this phase is complete

- [x] T002 Implement POSIX environment validation helper for `tar`, `gzip`, and `zip` commands in `scripts/make_seed_pack.sh`
- [x] T003 [P] Create CLI option parser (`-o/--output`, `--zip`, `-h/--help`) in `scripts/make_seed_pack.sh`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - 마이그레이션용 경량 Seed Pack 압축 생성 스크립트 실행 (Priority: P1) 🎯 MVP

**Goal**: Implement `scripts/make_seed_pack.sh` to package core files while excluding large models, virtualenv, and build artifacts into a lightweight archive (`dist/vllm_serv_seed.tar.gz` < 10MB).

**Independent Test**: `./make_seed_pack.sh` generates `dist/vllm_serv_seed.tar.gz` under 10MB containing only core source code and scripts.

- [x] T004 [P] [US1] Create unit tests for Seed Pack creation and exclusion rules in `tests/unit/test_seed_pack.py`
- [x] T005 [US1] Implement core tarball packaging logic with explicit `--exclude` rules (`models/*`, `.venv/*`, `.bin/*`, `logs/*`, `build/*`, `dist/*`, `__pycache__/*`, `.git/*`, `.pytest_cache/*`, `*.tar.gz`, `*.zip`) in `scripts/make_seed_pack.sh`
- [x] T006 [US1] Implement `--zip` format creation support and custom output path (`-o/--output`) handling in `scripts/make_seed_pack.sh`
- [x] T007 [US1] Create root executable symbolic link `./make_seed_pack.sh` pointing to `scripts/make_seed_pack.sh` with executable permissions
- [x] T008 [US1] Add archive file size check (<10MB) and migration guidance output in `scripts/make_seed_pack.sh`

**Checkpoint**: User Story 1 fully functional - `vllm_serv_seed.tar.gz` generated and verified independently.

---

## Phase 4: User Story 2 - 타 시스템에서 Seed Pack 압축 해제 및 setup.sh 프로젝트 구성 (Priority: P2)

**Goal**: Validate that extracting the Seed Pack archive on a target system and running `./setup.sh` successfully restores `uv` virtual environment and CUDA builds.

**Independent Test**: Extract `dist/vllm_serv_seed.tar.gz` into clean temporary sandbox and run `./setup.sh`; verify `llama_supports_gpu()` returns `True`.

- [x] T009 [P] [US2] Create integration test for Seed Pack extraction and `./setup.sh` restoration in `tests/integration/test_migration_pipeline.py`
- [x] T010 [US2] Verify `./setup.sh` required files list includes `scripts/make_seed_pack.sh` in `scripts/setup.sh`

**Checkpoint**: User Stories 1 AND 2 working independently.

---

## Phase 5: User Story 3 - 복원된 시스템의 start_server.sh 구동 및 모델 자동 서비스 개설 (Priority: P3)

**Goal**: Verify that starting `./start_server.sh` in a restored environment automatically downloads default model `qwen3.5-4b` and enters READY status with 100% VRAM offload.

**Independent Test**: Run `./start_server.sh` in restored environment without local models; verify auto-download and HTTP REST API readiness.

- [x] T011 [P] [US3] Create end-to-end integration test for restored `./start_server.sh` model auto-download in `tests/integration/test_migration_pipeline.py`

**Checkpoint**: All user stories functional independently and end-to-end.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation updates and test suite verification

- [x] T012 [P] Update `README.md` with Seed Pack migration guidelines and `./make_seed_pack.sh` CLI options
- [x] T013 Run full test suite `uv run pytest -v` and validate scenarios in `specs/019-seed-pack-generator/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories.
- **User Stories (Phases 3-5)**: All depend on Foundational phase completion.
  - Phase 3 (US1, P1) → Phase 4 (US2, P2) → Phase 5 (US3, P2).
- **Polish (Phase 6)**: Depends on all user stories being complete.

---

## Parallel Opportunities

- All Setup & Foundational tasks marked `[P]` can run in parallel.
- `T004 [P] [US1]` (unit test) can run in parallel with initial script setup.
- `T009 [P] [US2]` (integration test) can be developed independently of US1 polish.
- `T012 [P]` (README documentation) can run in parallel with Phase 6 polish.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) and Phase 2 (Foundational).
2. Complete Phase 3 (User Story 1 - `scripts/make_seed_pack.sh` & `./make_seed_pack.sh`).
3. **VALIDATE**: Run `./make_seed_pack.sh` and inspect `dist/vllm_serv_seed.tar.gz`.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready.
2. Add US1 → Seed Pack Generator → Validate MVP.
3. Add US2 → Target system extraction & `setup.sh` restoration → Validate.
4. Add US3 → Target system `start_server.sh` model auto-download → Validate.
5. Run Polish (Phase 6) & Quickstart scenarios.
