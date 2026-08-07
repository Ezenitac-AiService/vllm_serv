# Technical Research: 벤치마크 파이프라인 최적 모델 및 컨텍스트 윈도우 동적 선정 로직 정상화

**Feature Identifier**: `110-benchmark-model-selection-fix`  
**Date**: 2026-08-07  

---

## 1. Technical Context & Problem Analysis

### Identified Root Causes
1. **Schema Mismatch & False Fallback**:
   - `run_fine_grained_binary_search` returns dictionary keys: `"tpot_tok_per_sec"`, `"recommended_context_length"`, `"max_context_length"`, `"peak_vram_mb"`.
   - `evaluate_all_catalog_models` extracted values using missing keys: `"benchmark_tps"`, `"recommended_context_window"`, `"vram_used_mb"`.
   - Result: All supported models received `tps = 30.0` default fallback and `recommended_context_window = 4096` fallback.
   - Impact: Model selection loop (`if is_sup and tps > best_tps:`) always defaulted to the very first supported model in catalog (`gemma4-e2b`) and hardcoded context length `4096`.

2. **C-B-A Hybrid Selection Algorithm Requirement**:
   - User specification requires a balanced selection strategy evaluating:
     - **C (Model Quality & 8K Floor)**: Prefer larger models (9B > 4B > 2B) achieving `max_context_length >= 8192` with 8K -> 4K -> 2K Graceful Fallback.
     - **B (Composite Score)**: Rank tied candidates using $\text{Score} = \text{Param\_Weight} \times \text{TPS} \times \log_2(\text{recommended\_context\_length} / 2048) / (\text{peak\_vram\_mb} / 1024)$.
     - **A (Tie-Breaker)**: Fallback ordering by `recommended_context_length` ↓, `tpot_tok_per_sec` ↓, `peak_vram_mb` ↑.

---

## 2. Technical Decisions & Design Choices

### Decision 1: Unified Schema Access Helper
- **Approach**: Implement a safe dictionary accessor helper in `scripts/benchmark_context_window.py`:
  - `tps = res.get("tpot_tok_per_sec") or res.get("benchmark_tps") or (30.0 if res.get("is_supported") else 0.0)`
  - `rec_ctx = res.get("recommended_context_length") or res.get("max_context_length") or res.get("recommended_context_window") or 4096`
  - `vram_mb = res.get("peak_vram_mb") or res.get("vram_used_mb") or 0`
- **Rationale**: Guarantees zero-NPE/zero-KeyError fallback while strictly preferring exact binary search result values over default fallbacks.

### Decision 2: C-B-A Hybrid Model Sorting & Selection Engine
- **Approach**:
  1. Determine dynamic 8K floor: Try threshold 8192. If no candidate model has `rec_ctx >= 8192`, fallback to 4096, then 2048.
  2. For each supported model:
     - Determine `param_weight`: 9B/12B/27B -> 3.0, 4B -> 2.0, 2B -> 1.0.
     - Calculate `composite_score`:
       $$\text{Score} = \text{param\_weight} \times \text{tps} \times \log_2(\max(1, \text{rec\_ctx} / 2048)) / \max(1.0, \text{vram\_mb} / 1024.0)$$
  3. Sort supported models by tuple key:
     `(has_passed_ctx_floor, param_weight, composite_score, rec_ctx, tps, -vram_mb)` in descending order.
- **Rationale**: Satisfies user requirement for balancing model response speed (TPS), context window capacity (n_ctx), model quality (parameters), and GPU VRAM efficiency.

### Decision 3: Stage 4 Configuration Integration
- **Approach**: Ensure `evaluate_all_catalog_models` passes the dynamically calculated `rec_ctx` and `recommended_model` directly to `save_benchmark_profile` and updates `config/server_config.json`.
- **Rationale**: Guarantees that running `--force-benchmark` produces real dynamic settings in configuration files.

---

## 3. Alternatives Considered

| Alternative | Rationale for Rejection |
|-------------|-------------------------|
| Pure TPS Selection | Ignores model intelligence quality and context window size; small 2B models would always win over 4B/9B. |
| Hardcoded First Model | Broken behavior identified by user. |
| Pure Max Context Window | Ignores model parameter size and response speed. |
