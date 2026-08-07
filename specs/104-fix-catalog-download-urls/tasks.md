# Tasks: `config/model_catalog.json` HF 다운로드 URL 원인 분석, 리팩토링 및 404 오류 수렴 검증 (104-fix-catalog-download-urls)

**Input**: Design documents from `/specs/104-fix-catalog-download-urls/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project contract schema verification and configuration setup

- [X] T001 Verify contract schema `specs/104-fix-catalog-download-urls/contracts/catalog-url-schema.json` against `config/model_catalog.json` structure rules

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core repository verification that MUST be complete before metadata refactoring

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Verify current 14 models in `config/model_catalog.json` and ensure local file paths and schema keys remain intact before metadata refactoring

**Checkpoint**: Foundation ready - user story refactoring and TDD test tasks can now begin.

---

## Phase 3: User Story 1 - `model_catalog.json` HuggingFace Repo ID 및 파일명 실측 리팩토링 (Priority: P1) 🎯 MVP

**Goal**: Refactor `config/model_catalog.json` so that all 14 models have 100% valid 200 OK HuggingFace Hub `repo_id` and `filename` paths, ensuring Qwen 3.6 27B/35B, Instruct (`it`/`Instruct`) quantized `Q4_K_M` GGUF models, and text-only (`requires_mmproj: false`) Gemma 4 models.

**Independent Test**: Check that `gemma4-26b-a4b`, `qwen3.6-27b`, and `qwen3.6-35b-a3b` metadata in `config/model_catalog.json` point to verified 200 OK URLs and pass validation.

### Implementation for User Story 1

- [X] T003 [P] [US1] Refactor `gemma4-26b-a4b` metadata in `config/model_catalog.json` to point to `repo_id`: `unsloth/gemma-4-26B-A4B-it-GGUF` and `filename`: `gemma-4-26B-A4B-it-UD-Q4_K_M.gguf` with `requires_mmproj: false` and `clip_filename: null`
- [X] T004 [P] [US1] Refactor `qwen3.6-27b` metadata in `config/model_catalog.json` to point to `repo_id`: `unsloth/Qwen3.6-27B-GGUF` and `filename`: `Qwen3.6-27B-Q4_K_M.gguf`
- [X] T005 [P] [US1] Refactor `qwen3.6-35b-a3b` metadata in `config/model_catalog.json` to point to `repo_id`: `unsloth/Qwen3.6-35B-A3B-GGUF` and `filename`: `Qwen3.6-35B-A3B-UD-Q4_K_M.gguf`
- [X] T006 [US1] Audit and verify all remaining 11 models in `config/model_catalog.json` (`gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`, `qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b`, `gemma4-2b-text`, `gemma4-4b-text`, `gemma4-12b-text`, `bge-m3`, `bge-reranker-v2-m3`) to confirm Instruct (`it`/`Instruct`) quantized `Q4_K_M`/`Q8_0` GGUF paths

**Checkpoint**: User Story 1 complete - All 14 model catalog metadata entries in `config/model_catalog.json` updated with 200 OK HuggingFace Hub URLs.

---

## Phase 4: User Story 2 - 실체적 HF Hub URL 무결성 TDD 검증 수트 및 폴리싱 (Priority: P1)

**Goal**: Add live HTTP 200 OK verification unit test suite in `tests/unit/test_model_downloader.py` and verify `scripts/ensure_models.py` CLI execution.

**Independent Test**: Run `uv run pytest tests/unit/test_model_downloader.py` and `uv run scripts/ensure_models.py --all --check-only`.

### Implementation for User Story 2

- [X] T007 [P] [US2] Write unit test `test_model_catalog_hf_urls_valid` in `tests/unit/test_model_downloader.py` that iterates over all 14 catalog models in `config/model_catalog.json` and performs HEAD HTTP requests to verify 200 OK responses
- [X] T008 [US2] Write unit test `test_model_catalog_instruct_and_text_only_specs` in `tests/unit/test_model_downloader.py` to assert that Gemma 4 text-only models have `requires_mmproj == False` and `clip_filename == None`, and all LLM models are quantized GGUFs
- [X] T009 [US2] Execute CLI check `uv run scripts/ensure_models.py --all --check-only` in `scripts/ensure_models.py` to confirm zero 404 Client Errors for all 14 models

**Checkpoint**: User Story 2 complete - Live HTTP 200 OK TDD test suite operational and zero 404 errors verified.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final test suite validation and quickstart scenario execution

- [X] T010 [P] Run full unit test suite `uv run pytest tests/unit/` to verify zero regression across all modules
- [X] T011 Run quickstart validation scenarios in `specs/104-fix-catalog-download-urls/quickstart.md` to confirm end-to-end catalog download readiness

---

## Phase 6: Convergence

**Purpose**: Close remaining gaps identified by convergence assessment against spec, plan, and constitution.

- [X] T012 [US2] Tighten `quant_type` assertion in `test_model_catalog_instruct_and_text_only_specs` (`tests/unit/test_model_downloader.py:280`) to accept only `("q4_k_m", "q8_0")` per FR-003 (partial)
