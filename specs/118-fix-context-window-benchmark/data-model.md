# Data Model: 마이그레이션 RTX 3060 플랫폼 컨텍스트 윈도우 벤치마크 전수 평가 및 동적 KV 캐시 VRAM 오탐 수정

## 1. GQA Architecture Metadata Schema (ModelCatalogEntry)

`config/model_catalog.json` 내 모델별 아키텍처 파라미터 구조 정의.

```json
{
  "qwen3.5-2b": {
    "name": "Qwen 3.5 2B",
    "size_gb": 1.5,
    "quant_type": "q4_k_m",
    "n_layers": 24,
    "n_heads": 16,
    "n_head_kv": 8,
    "head_dim": 128,
    "max_n_ctx": 131072,
    "vram_est_mb": 2200,
    "task_type": "llm"
  },
  "qwen3.5-4b": {
    "name": "Qwen 3.5 4B",
    "size_gb": 2.5,
    "quant_type": "q4_k_m",
    "n_layers": 36,
    "n_heads": 32,
    "n_head_kv": 8,
    "head_dim": 128,
    "max_n_ctx": 131072,
    "vram_est_mb": 3950,
    "task_type": "llm"
  }
}
```

### Attributes:
- `n_layers` (integer): Transformer 레이어 수
- `n_heads` (integer): Attention query 헤더 수
- `n_head_kv` (integer): GQA key-value 헤더 수 (없거나 0인 경우 `n_heads`와 동일)
- `head_dim` (integer): 헤더 당 차원 수 (기본값 128)

---

## 2. KV Cache VRAM Estimation Function Interface

`estimate_kv_cache_vram()` 함수의 동적 파라미터 시그니처 및 산출식.

```python
def estimate_kv_cache_vram(
    n_layers: int = 36,
    n_heads: int = 32,
    head_dim: int = 128,
    n_ctx: int = 4096,
    bytes_per_element: float = 2.0,
    n_head_kv: Optional[int] = None
) -> int:
    kv_heads = n_head_kv if n_head_kv is not None and n_head_kv > 0 else n_heads
    total_bytes = 2 * n_layers * kv_heads * head_dim * n_ctx * bytes_per_element
    return max(1, int(total_bytes / (1024 * 1024)))
```

### Calculation Example (Qwen 3.5 2B @ n_ctx=16384):
- `n_layers` = 24
- `kv_heads` = 8 (GQA 2:1 축소)
- `head_dim` = 128
- `n_ctx` = 16384
- `total_bytes` = 2 * 24 * 8 * 128 * 16384 * 2.0 = 1,610,612,736 bytes = **1,536 MB** (기존 하드코딩 9,216MB 대비 약 83.3% 절감!)

---

## 3. Model Context Profiles Schema (`config/model_context_profiles.json`)

```json
{
  "generated_at": "2026-08-08T05:35:20Z",
  "system_hardware": {
    "gpu_name": "NVIDIA GeForce RTX 3060",
    "total_vram_mb": 12288,
    "is_cuda_available": true
  },
  "profiles": {
    "qwen3.5-2b": {
      "max_context_length": 13312,
      "recommended_context_length": 12800,
      "binary_search_steps": [
        {
          "step": 1,
          "tested_n_ctx": 8192,
          "real_vram_mb": 2360,
          "status": "PASS",
          "reason": "SUCCESS"
        }
      ],
      "peak_vram_mb": 2360,
      "tpot_tok_per_sec": 89.49,
      "scaling_tested": true,
      "is_supported": true,
      "failure_reason": "SUCCESS",
      "last_tested_at": "2026-08-08T05:35:20Z"
    }
  }
}
```
