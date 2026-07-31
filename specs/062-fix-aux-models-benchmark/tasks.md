# Tasks: 보조 모델(임베딩/리랭킹) 구동 및 품질 벤치마크 평가 개선

**Input**: Design documents from `/specs/062-fix-aux-models-benchmark/`

**Prerequisites**: [plan.md](file:///home/dev/storage/vllm_serv/specs/062-fix-aux-models-benchmark/plan.md), [spec.md](file:///home/dev/storage/vllm_serv/specs/062-fix-aux-models-benchmark/spec.md), [research.md](file:///home/dev/storage/vllm_serv/specs/062-fix-aux-models-benchmark/research.md), [data-model.md](file:///home/dev/storage/vllm_serv/specs/062-fix-aux-models-benchmark/data-model.md), [quickstart.md](file:///home/dev/storage/vllm_serv/specs/062-fix-aux-models-benchmark/quickstart.md)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and configuration alignment

- [x] T001 Verify project model catalog and server configuration in `config/model_catalog.json` and `config/server_config.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core model catalog task types and process manager helper methods

- [x] T002 Update auxiliary model task types (`embedding` for `bge-m3`, `rerank` for `bge-reranker-v2-m3`) in `config/model_catalog.json`
- [x] T003 [P] Add task type detection helper methods in `src/core/process_manager.py`

**Checkpoint**: Foundational model catalog definitions ready - user story implementation can begin

---

## Phase 3: User Story 1 - BGE M3 Embedding Model Serving & Inference (Priority: P1) 🎯 MVP

**Goal**: Enable BGE M3 (`bge-m3`) embedding model loading with `--embedding` CLI flag and verify `/v1/embeddings` vector inference during benchmark execution.

**Independent Test**: Run `uv run python scripts/benchmark_quality.py --real` or unit test to verify `bge-m3` produces valid embedding vectors without inference failure.

### Tests for User Story 1 ⚠️

- [x] T004 [P] [US1] Write unit test for BGE M3 embedding process spawning and `/v1/embeddings` payload verification in `tests/unit/test_auxiliary_embedding.py`

### Implementation for User Story 1

- [x] T005 [US1] Update `ProcessManager` in `src/core/process_manager.py` to inject `--embedding` CLI flag when spawning `bge-m3`
- [x] T006 [US1] Update `AuxiliaryModelManager` in `src/core/auxiliary_manager.py` for port 8090 embedding instance health polling
- [x] T007 [US1] Update `scripts/benchmark_quality.py` to route embedding models (`task_type == "embedding"`) to `/v1/embeddings` HTTP POST requests
- [x] T008 [US1] Verify US1 unit and embedding inference tests pass (`uv run pytest tests/unit/test_auxiliary_embedding.py`)
 
 Checkpoint: User Story 1 fully functional — BGE M3 embedding inference succeeded.
 
 ---
 
 ## Phase 4: User Story 2 - BGE Reranker v2 M3 Cross-Encoder Serving & Healthcheck (Priority: P2)
 
 Goal: Enable BGE Reranker v2 M3 (`bge-reranker-v2-m3`) Cross-Encoder serving with `--reranking` CLI flags and adaptive healthcheck polling.
 
 Independent Test: Spawn `bge-reranker-v2-m3` and verify healthcheck readiness within 15 seconds and valid reranking response.
 
 ### Tests for User Story 2 ⚠️
 
 - [x] T009 [P] [US2] Write unit test for BGE Reranker v2 M3 process spawning and `/rerank` payload verification in `tests/unit/test_auxiliary_reranker.py`
 
 ### Implementation for User Story 2
 
 - [x] T010 [US2] Update `ProcessManager` in `src/core/process_manager.py` to inject `--reranking` and `--embedding` CLI flags when spawning `bge-reranker-v2-m3`
 - [x] T011 [US2] Update `AuxiliaryModelManager` in `src/core/auxiliary_manager.py` for port 8091 reranker instance adaptive healthcheck polling
 - [x] T012 [US2] Update `scripts/benchmark_quality.py` to handle `task_type == "rerank"` and evaluate reranker health and inference
 - [x] T013 [US2] Verify US2 unit and reranker tests pass (`uv run pytest tests/unit/test_auxiliary_reranker.py`)
 
 Checkpoint: User Story 2 fully functional — BGE Reranker v2 M3 serving and healthcheck verified.
 
 ---
 
 ## Phase 5: User Story 3 - Benchmark Multi-Model Restoration, Preflight Guard & Dashboard Dynamic Paths (Priority: P3)
 
 Goal: Ensure post-benchmark restoration spawns detached background processes for `qwen3.5-4b`, `bge-m3`, and `bge-reranker-v2-m3`, add 503 preflight guard on unready backend, and convert dashboard API paths to `window.location.origin`.
 
 Independent Test: Run `scripts/benchmark_quality.py --real`, verify script completion, verify `./status_server.sh` shows `RUNNING` status, and run Playwright E2E browser test for dashboard UI.
 
 ### Tests for User Story 3 ⚠️
 
 - [x] T014 [P] [US3] Write integration test for proxy preflight guard returning 503 on unready backend in `tests/integration/test_preflight_proxy_guard.py`
 - [x] T015 [P] [US3] Write integration test for post-benchmark detached co-loading restoration in `tests/integration/test_coloading_restoration.py`
 - [x] T016 [P] [US3] Write Playwright E2E browser test for dashboard dynamic API paths in `tests/e2e/test_dashboard_timeout_prevention.py`
 
 ### Implementation for User Story 3
 
 - [x] T017 [US3] Implement backend health preflight guard in `src/api/routes/inference_api.py` and `src/api/routes/dashboard_api.py` (return 503 immediately when 8089 is initializing)
 - [x] T018 [US3] Implement detached background process restoration in `scripts/benchmark_quality.py` `finally:` block for `qwen3.5-4b`, `bge-m3`, and `bge-reranker-v2-m3`
 - [x] T019 [US3] Convert all static frontend dashboard API calls in `src/static/` (or HTML/JS template assets) to use `window.location.origin` dynamic relative paths
 - [x] T020 [US3] Verify US3 integration and Playwright E2E tests pass (`uv run pytest tests/integration/` and `uv run pytest tests/e2e/`)

**Checkpoint**: All user stories implemented — benchmark execution, multi-model restoration, preflight guard, and dashboard UI fully functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Full system verification, benchmark report generation, and complete regression test suite

- [x] T021 Run full quality benchmark in real GPU mode (`uv run python scripts/benchmark_quality.py --auto-download --real`) and verify report generation in `data/reports/analysis_report_quality.md`
- [x] T022 Validate server daemon liveness and hardware report (`./status_server.sh`) after benchmark completion
- [x] T023 Run quickstart validation scenarios documented in `quickstart.md`
- [x] T024 Run full regression test suite (`uv run pytest`) to ensure 100% Green Pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1) → User Story 2 (P2) → User Story 3 (P3)
- **Polish (Phase 6)**: Depends on all user stories being complete

### Parallel Opportunities

- T003, T004, T009, T014, T015, T016 can run in parallel (unit/integration test files)
- Implementation tasks within each story follow TDD order: test written → code implemented → test verified

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup (Phase 1) and Foundational (Phase 2)
2. Complete User Story 1 (Phase 3)
3. Validate BGE M3 embedding inference independently

### Incremental Delivery

1. Deliver MVP (BGE M3 Embedding serving)
2. Add User Story 2 (BGE Reranker v2 M3 serving)
3. Add User Story 3 (Post-benchmark restoration, preflight guard, dashboard dynamic paths)
4. Execute full regression suite & real GPU benchmark validation

---

## Notes

- Strict checklist format: `- [ ] TaskID [P?] [Story?] Description with file path`
- Every task includes an explicit, absolute or project-relative file path
- Follows Constitution Principles: zero mock in implementation code, real GPU verification, `uv run` environment management, full regression testing & Playwright E2E discipline.
