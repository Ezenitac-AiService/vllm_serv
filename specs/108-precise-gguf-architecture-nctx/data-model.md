# Data Model: Precise GGUF Architecture & Uncapped Model Range

**Feature Identifier**: `108-precise-gguf-architecture-nctx`  
**Date**: 2026-08-07  

---

## Data Entities

### 1. `GgufArchitectureParams` (Pydantic Model)
Represents the exact architectural metadata of a GGUF model.

- `model_id`: `str` (Primary Key, e.g., "gemma4-e2b")
- `n_layers`: `int` (Number of Transformer layers / blocks)
- `n_heads`: `int` (Number of Query attention heads)
- `n_head_kv`: `int` (Number of Key/Value attention heads for GQA/MQA)
- `head_dim`: `int` (Dimension of each head)
- `bytes_per_elem`: `float` (Default 2.0 for FP16, 1.0 for FP8, 0.5 for INT4)
- `max_rope_n_ctx`: `int` (Maximum RoPE context length from GGUF metadata, e.g., 32768, 131072, 1048576)

---

### 2. `DynamicSearchState` (Pydantic Model)
Encapsulates state during binary search execution.

- `low`: `int` (Current lower bound, min 2048)
- `high`: `int` (Current upper bound, dynamically expanded)
- `step_size`: `int` (Dynamically calculated step size using log formula)
- `free_vram_ratio`: `float` (Ratio of remaining free VRAM after test step)
- `re_expanded_count`: `int` (Number of times upper bound was dynamically expanded)
