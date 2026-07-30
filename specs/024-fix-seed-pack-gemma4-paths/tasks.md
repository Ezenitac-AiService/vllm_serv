# Tasks: 코드베이스 전체 모델 경로 하드코딩 제거 및 Gemma 4 카탈로그 정합성 보장 (024-fix-seed-pack-gemma4-paths)

**Input**: Design documents from `/specs/024-fix-seed-pack-gemma4-paths/`

**Prerequisites**: [plan.md](file:///home/dev/storage/vllm_serv/specs/024-fix-seed-pack-gemma4-paths/plan.md), [spec.md](file:///home/dev/storage/vllm_serv/specs/024-fix-seed-pack-gemma4-paths/spec.md), [research.md](file:///home/dev/storage/vllm_serv/specs/024-fix-seed-pack-gemma4-paths/research.md), [data-model.md](file:///home/dev/storage/vllm_serv/specs/024-fix-seed-pack-gemma4-paths/data-model.md), [quickstart.md](file:///home/dev/storage/vllm_serv/specs/024-fix-seed-pack-gemma4-paths/quickstart.md)

**Tests**: 테스트 코드는 헌장 II원칙(테스트 주도 개발 및 품질 보증)에 따라 모든 기능 변경 시 검증과 함께 작성 및 실행됩니다.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [TaskID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (`[US1]`, `[US2]`)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project catalog & specification layout verification

- [x] T001 Verify project structure and catalog file at `config/model_catalog.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core model catalog metadata rectification and path resolution infrastructure that MUST be complete before user story scripts can execute

**⚠️ CRITICAL**: All user story tasks depend on the catalog metadata and `ConfigManager` resolution in this phase.

- [x] T002 [P] Rectify `config/model_catalog.json` Gemma 4 entries (`gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`) with correct `repo_id`, `filename`, `clip_filename`, `target_dir`, `model_path`, and `clip_path`
- [x] T003 [P] Implement legacy key alias resolution (`gemma4-2b` -> `gemma4-e2b`, `gemma4-4b` -> `gemma4-e4b`) and absolute path resolver in `src/core/config_manager.py`
- [x] T004 [P] Update `src/core/model_downloader.py` to auto-create target directory (`os.makedirs`) and handle public HF downloads gracefully without mandatory `HF_TOKEN`

**Checkpoint**: Foundation ready - catalog metadata and base path resolution complete.

---

## Phase 3: User Story 1 - 카탈로그 및 코드베이스 전체 모델 경로 하드코딩 일원화 (Priority: P1) 🎯 MVP

**Goal**: Remove hardcoded dictionaries (`SUPPORTED_MODELS`) and invalid HF repo IDs in core config/download components and enforce `ConfigManager` SSOT across all model loading pipelines.

**Independent Test**: `uv run pytest tests/unit/test_config_manager.py tests/unit/test_model_downloader.py tests/integration/test_gemma4_serving.py` and `uv run python src/scripts/download_models.py` without HF_TOKEN errors or 404s.

### Tests for User Story 1 ⚠️

- [x] T005 [P] [US1] Add unit tests for `ConfigManager` SSOT catalog reading and key alias resolution in `tests/unit/test_config_manager.py`
- [x] T006 [P] [US1] Add unit tests for `ModelDownloader` absolute pathing and optional HF token handling in `tests/unit/test_model_downloader.py`

### Implementation for User Story 1

- [x] T007 [US1] Remove hardcoded `SUPPORTED_MODELS` dict and delegate model listing to `ConfigManager` in `src/core/config.py`
- [x] T008 [US1] Refactor model downloader script `src/scripts/download_models.py` to use `ConfigManager` and `ModelDownloader` instead of `SUPPORTED_MODELS`
- [x] T009 [US1] Update `src/core/process_manager.py` to perform project-root absolute path resolution for `target_dir`, `model_path`, and `clip_path`
- [x] T010 [US1] Update integration tests in `tests/integration/test_gemma4_serving.py` to match `gemma4-e2b` SSOT catalog paths and key names

**Checkpoint**: At this point, User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - `scripts/benchmark_quality.py` 및 레거시 벤치마크 스크립트 정상 동작 (Priority: P2)

**Goal**: Update all benchmark scripts (`scripts/benchmark_quality.py`, `src/scripts/benchmark.py`, `src/scripts/benchmark_128k.py`, `src/scripts/benchmark_context_scaling.py`) to query `ConfigManager` SSOT instead of hardcoding model lists and repo IDs.

**Independent Test**: Run `uv run python scripts/benchmark_quality.py` and `uv run python src/scripts/benchmark.py` without model ID mismatch or file missing errors.

### Tests for User Story 2 ⚠️

- [x] T011 [P] [US2] Add integration tests for context scaling and serving switch with updated catalog keys in `tests/integration/test_context_scaling.py` and `tests/integration/test_serving_switch.py`

### Implementation for User Story 2

- [x] T012 [P] [US2] Update `scripts/benchmark_quality.py` to dynamically load `MODELS_CATALOG` from `ConfigManager().get_model_catalog()` instead of hardcoded list
- [x] T013 [P] [US2] Update `src/scripts/benchmark.py` to fetch model keys dynamically from `ConfigManager`
- [x] T014 [P] [US2] Update `src/scripts/benchmark_128k.py` to query `gemma4-e2b` from `ConfigManager`
- [x] T015 [P] [US2] Update `src/scripts/benchmark_context_scaling.py` to query model list from `ConfigManager`

**Checkpoint**: At this point, User Stories 1 AND 2 work independently and smoothly.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final verification, codebase audit, and test execution

- [x] T016 [P] Perform codebase-wide grep audit for any remaining hardcoded model IDs/paths (`gemma4-2b`, etc.)
- [x] T017 Run complete pytest suite (`uv run pytest tests/`) to ensure 100% test pass rate across unit and integration tests
- [x] T018 Execute quickstart validation scenarios documented in `specs/024-fix-seed-pack-gemma4-paths/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1) → User Story 2 (P2)
- **Polish (Final Phase)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 SSOT catalog provider

### Parallel Opportunities

- All Foundational tasks marked `[P]` (T002, T003, T004) can run in parallel
- Unit tests T005, T006 can run in parallel
- Benchmark script refactoring tasks marked `[P]` (T012, T013, T014, T015) can run in parallel

---

## Parallel Example: User Story 1 & 2

```bash
# Foundational parallel execution:
Task: T002 "Rectify config/model_catalog.json Gemma 4 entries"
Task: T003 "Implement legacy key alias resolution in src/core/config_manager.py"
Task: T004 "Update src/core/model_downloader.py to auto-create target directory"

# Benchmark parallel execution (Phase 4):
Task: T012 "Update scripts/benchmark_quality.py"
Task: T013 "Update src/scripts/benchmark.py"
Task: T014 "Update src/scripts/benchmark_128k.py"
Task: T015 "Update src/scripts/benchmark_context_scaling.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Verify `uv run pytest tests/` and `uv run python src/scripts/download_models.py`
5. Proceed to User Story 2 and Polish
