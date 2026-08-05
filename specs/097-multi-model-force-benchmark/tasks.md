# Tasks: Full Multi-Model GPU Benchmarking & Forced Optimization Pipeline

**Feature**: 097-multi-model-force-benchmark  
**Status**: IN_PROGRESS  

---

## Phase 1: Setup & Foundational

- [ ] T001 Inspect `config/model_catalog.json` and candidate LLM models parsing in `scripts/benchmark_context_window.py`

---

## Phase 2: User Story 1 - Multi-Model Catalog Evaluation & Forced Benchmarking

- [ ] T002 [P] [US1] Add `--force-benchmark` and catalog iteration logic in `scripts/benchmark_context_window.py` to evaluate all candidate LLM models
- [ ] T003 [P] [US1] Update `scripts/setup.sh` Step 2.8 and Step 4.5 to pass `--force-benchmark` down to `benchmark_context_window.py`
- [ ] T004 [P] [US1] Implement automatic selection of optimal serving model and context window determination via fine-grained binary search in `scripts/benchmark_context_window.py`

---

## Phase 3: Polish & Validation

- [ ] T005 [P] Run `./setup.sh --force-benchmark` validation scenario per `quickstart.md`
- [ ] T006 [P] Update unit test suite in `tests/unit/test_setup_benchmark_integration.py` to test multi-model forced benchmark catalog iteration

---

## Dependencies & Execution Order

- **Phase 1**: Setup (Catalog inspection)
- **Phase 2**: User Story 1 (Multi-model benchmark & setup.sh propagation)
- **Phase 3**: End-to-End Validation & Unit Test Pass

---

## Implementation Strategy

1. **MVP First**: Update `scripts/benchmark_context_window.py` to iterate through all candidate LLMs in `config/model_catalog.json`.
2. **Incremental Delivery**: Update `scripts/setup.sh` to pass `--force-benchmark` to Step 2.8 and Step 4.5, run validation, and update unit tests.
