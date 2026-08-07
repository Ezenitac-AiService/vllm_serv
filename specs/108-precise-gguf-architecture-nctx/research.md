# Technical Research: Precise GGUF Architecture & Uncapped Model Range

**Feature Identifier**: `108-precise-gguf-architecture-nctx`  
**Date**: 2026-08-07  

---

## 1. GQA (Grouped Query Attention) VRAM Reverse Calculation Formula

### Decision
Calculate KV cache VRAM per token using the exact number of Key/Value heads ($n_{\text{head\_kv}}$) rather than total Query heads ($n_{\text{heads}}$):
$$\text{KV\_bytes\_per\_token} = 2 \times n_{\text{layers}} \times n_{\text{head\_kv}} \times head\_dim \times \text{bytes\_per\_elem}$$

For FP16/BF16 (`bytes_per_elem = 2`), FP8 (`bytes_per_elem = 1`), INT4 (`bytes_per_elem = 0.5`).

### Rationale
Gemma 4 E2B uses 18 layers, 8 Query heads, but only 1 KV head (`n_head_kv = 1`) with `head_dim = 256`.  
Using the old 7B fallback formula ($n_{\text{heads}} = 32$) resulted in $0.56$ MB/token. The exact GQA formula evaluates to $0.018$ MB/token (a 30x reduction in KV cache memory usage!).

---

## 2. Dynamic Upper Bound Re-Expansion Algorithm

### Decision
When the binary search completes or tests the initial upper bound $high$ with `PASS`, check remaining free VRAM ratio:
$$\text{free\_ratio} = \frac{\text{usable\_vram} - \text{real\_vram\_mb}}{\text{usable\_vram}}$$
If $\text{free\_ratio} \ge 0.50$ and $high < \text{model\_max\_rope}$, re-expand the upper bound:
$$high' = \min(high \times 2, \text{model\_max\_rope})$$
and continue the binary search loop seamlessly.

---

## 3. Logarithmic Dynamic Binary Search Step Scaling

### Decision
Calculate the step size dynamically using log-base-2 scaling instead of fixed hardcoded step constants:
$$\text{step} = \max\left(512, 2^{\lfloor \log_2(high / 64) \rfloor}\right)$$

- For $high = 16384$: $\text{step} = 256 \to 512$
- For $high = 131072$ (128K): $\text{step} = 2048$
- For $high = 1048576$ (1M): $\text{step} = 16384$

---

## 4. Metadata Fallback Hierarchy (SSOT)

1. `config/model_catalog.json` explicit parameters (`n_layers`, `n_head_kv`, `head_dim`, `quant_type`)
2. GGUF file binary header parser (`gguf_header` struct: `llama.block_count`, `llama.attention.head_count_kv`, `llama.attention.key_length`)
3. Dynamic log-scaled fallback formula without static hardcoded magic numbers
