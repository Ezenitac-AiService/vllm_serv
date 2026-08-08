# Tasks: 마이그레이션 RTX 3060 플랫폼 컨텍스트 윈도우 벤치마크 전수 평가 및 동적 KV 캐시 VRAM 오탐 수정

**Input**: Design documents from `/specs/118-fix-context-window-benchmark/`  
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/  

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Includes exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify GQA metadata fields and base environment

- [x] T001 Verify GQA metadata fields (`n_layers`, `n_heads`, `n_head_kv`, `head_dim`) in `config/model_catalog.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core `estimate_kv_cache_vram()` GQA calculator foundation

- [x] T002 Ensure `estimate_kv_cache_vram()` in `src/core/gpu_detector.py` calculates exact GQA KV cache VRAM using `n_head_kv / n_heads` ratio

---

## Phase 3: User Story 1 - 동적 KV 캐시 추정기의 모델별 GQA 아키텍처 정밀 반영 (Priority: P1) 🎯 MVP

**Goal**: `ProcessManager` 사전 검사 및 KV 캐시 추정기(`estimate_kv_cache_vram`)에서 모델별 실제 GQA 아키텍처 파라미터를 동적 적용하여 16K 스케일링에서의 15.2GB 오탐 VRAM 차단 결함을 해결한다.

**Independent Test**: `uv run pytest tests/unit/test_benchmark_context_window.py -k test_estimate_vram_usage_uses_model_gqa_architecture`

### Implementation for User Story 1

- [x] T003 [P] [US1] Update `ProcessManager.estimate_vram_usage` in `src/core/process_manager.py` to dynamically fetch model GQA parameters from catalog and GGUF header
- [x] T004 [P] [US1] Update `ProcessManager.spawn_process` pre-flight VRAM check in `src/core/process_manager.py` to pass model GQA parameters into `estimate_kv_cache_vram()`
- [x] T005 [P] [US1] Add unit test in `tests/unit/test_benchmark_context_window.py` verifying GQA VRAM estimation for 2B/4B models at `n_ctx=16384`

**Checkpoint**: User Story 1 complete - 2B/4B models pass 16K context pre-flight checks without false 15.2GB OOM blocks.

---

## Phase 4: User Story 2 - 컨텍스트 윈도우 벤치마크 CLI 카탈로그 전수 모델 평가 모드 지원 (Priority: P1) 🎯 MVP

**Goal**: `scripts/benchmark_context_window.py` CLI에 `--all` 인자를 추가하여 카탈로그 내 모든 LLM 가용 모델을 순차 평가하고 `config/model_context_profiles.json` 프로파일을 반영한다.

**Independent Test**: `MOCK_LLAMA_SERVER=1 uv run python scripts/benchmark_context_window.py --fine-grained --all`

### Implementation for User Story 2

- [x] T006 [P] [US2] Implement CLI `--all` flag and catalog model iteration loop in `scripts/benchmark_context_window.py`
- [x] T007 [P] [US2] Add unit test in `tests/unit/test_benchmark_context_window.py` verifying CLI `--all` flag all-model evaluation

**Checkpoint**: User Story 2 complete - `--all` CLI flag evaluates all LLM models in catalog sequentially.

---

## Phase 5: User Story 3 - 품질-컨텍스트 종합 벤치마크(`benchmark_quality.py`) 스케일링 루프 정밀화 (Priority: P2)

**Goal**: `scripts/benchmark_quality.py` [Step 5.1] 스케일링 측정 루프의 VRAM Pre-flight 체크를 동적 GQA 추정기로 연동하여 15.2GB 오탐 실패를 방지한다.

**Independent Test**: `MOCK_LLAMA_SERVER=1 uv run python scripts/benchmark_quality.py`

### Implementation for User Story 3

- [x] T008 [P] [US3] Update Step 5.1 context scaling loop in `scripts/benchmark_quality.py` to use dynamic GQA VRAM estimation

**Checkpoint**: User Story 3 complete - `benchmark_quality.py` scaling loop runs without false OOM skips.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Full regression suite validation and quickstart scenario checks

- [x] T009 Run full unit test suite via `uv run pytest tests/unit/ --ignore=tests/unit/test_legacy_extraction_llm.py --ignore=tests/unit/test_e2e_serving.py --ignore=tests/unit/test_embedding_reranker_serving.py`
- [x] T010 Execute end-to-end validation scenarios documented in `specs/118-fix-context-window-benchmark/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) completion
- **User Story 2 (Phase 4)**: Can run in parallel with US1 after Foundational completion
- **User Story 3 (Phase 5)**: Depends on US1 completion
- **Polish (Phase 6)**: Depends on Phase 3 through Phase 5 completion

---

## Implementation Strategy

### MVP Scope

1. Complete Phase 1 (Setup) & Phase 2 (Foundational)
2. Complete Phase 3 (US1 - Dynamic GQA VRAM Estimation in `process_manager.py`)
3. Complete Phase 4 (US2 - CLI `--all` Flag in `benchmark_context_window.py`)
4. Validate MVP with `uv run pytest tests/unit/test_benchmark_context_window.py`
5. Complete Phase 5 (US3) & Phase 6 (Regression Suite)
