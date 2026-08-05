# Tasks: Qwen 및 Gemma 4 대형/양자화 모델 카탈로그 확장 및 제외 파이프라인 검증 (101-add-qwen-heavy-models-catalog)

**Input**: Design documents from `/specs/101-add-qwen-heavy-models-catalog/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and JSON schema contracts setup

- [X] T001 Verify contract schema `specs/101-add-qwen-heavy-models-catalog/contracts/model-catalog-schema.json` against `config/model_catalog.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Model catalog expansion that MUST be complete before user stories can be tested

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Update `config/model_catalog.json` to include 6 new models (`qwen3.6-27b`, `qwen3.6-35b-a3b`, `gemma4-26b-a4b`, `gemma4-2b-text`, `gemma4-4b-text`, `gemma4-12b-text`)
- [X] T003 [P] Update HuggingFace Hub download mapping in `src/core/model_downloader.py`

**Checkpoint**: Model catalog metadata expanded (14 models total).

---

## Phase 3: User Story 1 - Qwen 및 Gemma 4 대형/텍스트 전용 모델 카탈로그 수록 및 확장성 확보 (Priority: P1) 🎯 MVP

**Goal**: Integrate new model metadata into catalog and verify downloader / schema compliance for all 14 models.

**Independent Test**: `uv run pytest tests/unit/test_model_downloader.py` & JSON schema validation pass.

### Tests for User Story 1

- [X] T004 [P] [US1] Add unit test for 14 model catalog items & HuggingFace downloader path resolution in `tests/unit/test_model_downloader.py`

### Implementation for User Story 1

- [X] T005 [US1] Update catalog downloader reconciliation logic in `src/core/model_downloader.py`
- [X] T006 [US1] Update dynamic model catalog keys query in `scripts/ensure_models.py` (ensure `requires_mmproj: false` text-only models skip CLIP projector integrity checks)

**Checkpoint**: User Story 1 complete - all 14 models defined, loaded, and verified via unit tests.

---

## Phase 4: User Story 2 - setup.sh 파이프라인에서 VRAM 초과 대형 모델의 정밀 배제 및 오탐 없는 진단 검증 (Priority: P2)

**Goal**: Verify benchmark candidate evaluation safely excludes heavy models exceeding Usable VRAM with `is_supported: false` and `CUDA OOM Risk` failure reason.

**Independent Test**: `uv run pytest tests/unit/test_benchmark_context_window.py` & `./setup.sh --force-benchmark`.

### Tests for User Story 2

- [X] T007 [P] [US2] Add unit test for candidate LLM models filtering (12 LLMs) & Pre-flight Usable VRAM check (covering multi-tier 8G/11G/24G/32G/40G/80G VRAM parametric testing) in `tests/unit/test_benchmark_context_window.py`

### Implementation for User Story 2

- [X] T008 [US2] Verify `get_candidate_llm_models()` in `scripts/benchmark_context_window.py` dynamically loads all 12 candidate LLM models
- [X] T009 [US2] Verify pre-flight VRAM threshold calculation (`Usable VRAM < Base VRAM`) in `scripts/benchmark_context_window.py` to record `is_supported: false` and `CUDA OOM Risk` without throwing exceptions

**Checkpoint**: User Story 2 complete - heavy models safely excluded during benchmark, valid model selected for serving.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and regression testing

- [ ] T010 [P] Run full unit test suite `uv run pytest tests/unit/`
- [ ] T011 Run quickstart validation scenario (`./setup.sh --force-benchmark`) and verify clean completion without process crashes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on User Story 1 completion
- **Polish (Phase 5)**: Depends on User Story 1 & 2 completion

### Parallel Opportunities

- T003, T004, T007, T010 can run in parallel (different files, independent tests).

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & 2 (Catalog expansion)
2. Complete Phase 3 (User Story 1 - Unit test & catalog verification)
3. Validate User Story 1 independently

### Full Feature Delivery

1. Complete User Story 1 (Catalog expansion)
2. Complete User Story 2 (Benchmark safe exclusion)
3. Run Phase 5 regression tests & `./setup.sh --force-benchmark`
