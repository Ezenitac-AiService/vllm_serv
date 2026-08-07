# Quickstart Validation Guide: Precise GGUF Architecture & Uncapped Model Range

**Feature Identifier**: `108-precise-gguf-architecture-nctx`  
**Date**: 2026-08-07  

---

## Validation Scenario 1: GQA Architecture GGUF Metadata Extraction Test

Execute the unit test verifying GQA KV head parameter extraction:
```bash
uv run pytest tests/unit/test_gpu_detector.py -k test_calculate_max_allocatable_n_ctx_gqa
```
**Expected Outcome**:
For a 2B model with `n_layers=18, n_head_kv=1, head_dim=256`, `calculate_max_allocatable_n_ctx` calculates maximum allocatable context window > 32768 on 11GB VRAM.

---

## Validation Scenario 2: Uncapped Range Re-expansion Execution Test

Execute fine-grained benchmark on `gemma4-e2b`:
```bash
uv run python scripts/benchmark_context_window.py --model gemma4-e2b --fine-grained
```
**Expected Outcome**:
The search range dynamically expands beyond 11264 up to 32768 (or OOM limit), populating `max_context_length >= 32768` in `config/model_context_profiles.json`.

---

## Validation Scenario 3: Full Regression Suite Execution

Run all unit tests across the repository:
```bash
uv run pytest tests/unit/
```
**Expected Outcome**: 100% PASS rate across all unit tests.
