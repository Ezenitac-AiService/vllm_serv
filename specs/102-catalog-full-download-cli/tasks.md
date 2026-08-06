# Tasks: `scripts/ensure_models.py` 전체/특정 모델 다운로드 CLI 옵션 확장 (102-catalog-full-download-cli)

**Input**: Design documents from `/specs/102-catalog-full-download-cli/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and JSON schema contracts verification

- [X] T001 Verify contract schema `specs/102-catalog-full-download-cli/contracts/ensure-models-cli-schema.json` against CLI parser requirements in `scripts/ensure_models.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core model target resolver function that MUST be complete before user stories can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Implement `resolve_target_models(all_flag: bool, model_arg: Optional[str])` helper function in `scripts/ensure_models.py`

**Checkpoint**: Foundation ready - user story CLI option handlers can now be implemented.

---

## Phase 3: User Story 1 - 카탈로그 전체 모델 일괄 점검 및 다운로드 옵션 (`--all`) (Priority: P1) 🎯 MVP

**Goal**: Enable `--all` / `--download-all` CLI option in `scripts/ensure_models.py` to inspect and download all 14 models defined in `config/model_catalog.json`.

**Independent Test**: `uv run scripts/ensure_models.py --all --check-only` & `uv run pytest tests/unit/test_ensure_models_cli.py`.

### Tests for User Story 1

- [X] T003 [P] [US1] Create unit tests for `--all` flag parsing & target model resolution (14 models) in `tests/unit/test_ensure_models_cli.py`

### Implementation for User Story 1

- [X] T004 [US1] Add `--all` and `--download-all` options to `argparse` in `scripts/ensure_models.py`
- [X] T005 [US1] Update `main()` and `ensure_all_models()` in `scripts/ensure_models.py` to pass `all_flag` and process all 14 catalog models

**Checkpoint**: User Story 1 complete - all 14 catalog models can now be checked and downloaded via `--all`.

---

## Phase 4: User Story 2 - 특정 지정 모델 핀포인트 점검 및 다운로드 옵션 (`--model <MODEL_ID>`) (Priority: P2)

**Goal**: Enable `--model <MODEL_ID>` (single or comma-separated) flag in `scripts/ensure_models.py` with mutual exclusion error (exit code 2) against `--all` and unknown model ID check (exit code 1).

**Independent Test**: `uv run scripts/ensure_models.py --model qwen3.6-27b --check-only` & error handling unit tests in `tests/unit/test_ensure_models_cli.py`.

### Tests for User Story 2

- [X] T006 [P] [US2] Add unit tests for `--model` single/comma-separated parsing, mutual exclusion error (exit code 2), and invalid model ID error (exit code 1) in `tests/unit/test_ensure_models_cli.py`

### Implementation for User Story 2

- [X] T007 [US2] Add `--model` argument to `argparse` in `scripts/ensure_models.py`
- [X] T008 [US2] Add mutual exclusion check (`--all` and `--model` specified together) in `scripts/ensure_models.py` to print error and exit with code 2
- [X] T009 [US2] Add invalid model ID validation check in `scripts/ensure_models.py` to print `[ERROR] Unknown model_id: <ID>` and exit with code 1

**Checkpoint**: User Story 2 complete - specific models can be targeted via `--model`, with precise CLI error exit codes.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final regression testing and quickstart validation

- [X] T010 [P] Run full unit test suite `uv run pytest tests/unit/`
- [X] T011 Run quickstart validation scenarios (`specs/102-catalog-full-download-cli/quickstart.md`) and verify CLI exit codes (0, 1, 2)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on User Story 1 completion
- **Polish (Phase 5)**: Depends on User Story 1 & 2 completion

### Parallel Opportunities

- T003, T006, T010 can run in parallel (different test functions / test files).

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & 2 (Setup & `resolve_target_models`)
2. Complete Phase 3 (User Story 1 - `--all` flag implementation and test)
3. Validate User Story 1 independently with `--all --check-only`

### Full Feature Delivery

1. Complete User Story 1 (`--all` flag)
2. Complete User Story 2 (`--model` flag & mutual exclusion / invalid ID checks)
3. Run Phase 5 regression tests & quickstart validation scenarios

---

## Phase 6: Convergence

- [X] T012 Add explicit `downloader.reconcile_catalog_metadata(model_id)` invocation upon download completion in `scripts/ensure_models.py` per FR-005 (partial)
- [X] T013 Add `--download-all` alias CLI test and direct `ensure_all_models` test cases in `tests/unit/test_ensure_models_cli.py` per FR-001, DoD-002 (partial)
- [X] T014 Execute and verify full unit test suite regression pass `uv run pytest tests/unit/` per DoD-003, Constitution VII (partial)


