# Interface Contract: Benchmark Context Window CLI & Profile Cache API

## 1. CLI Executable Contract: `scripts/benchmark_context_window.py`

### Options & Flags

```bash
uv run python scripts/benchmark_context_window.py [OPTIONS]
```

| Flag | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--model` | String | `qwen3.5-4b` | 탐색할 타겟 모델 ID |
| `--force-benchmark` | Flag | `False` | 카탈로그 전체 LLM 후보 모델 대상 실측 이진 탐색 전체 수행 |
| `--fine-grained` | Flag | `False` | 지정 모델 대상 5단계 정밀 이진 탐색(`range(5)`) 수행 |
| `--skip-benchmark` | Flag | `False` | 3단계 실측 탐색 스킵 및 기존 설정 보존 |
| `--json` | Flag | `False` | 탐색 결과를 JSON 포맷으로 표준 출력에 출력 |

### Output JSON Format Specification (`--json`)

```json
{
  "recommended_model": "qwen3.5-2b",
  "max_context_length": 10240,
  "recommended_context_length": 8192,
  "binary_search_steps": [
    {
      "step": 1,
      "tested_n_ctx": 10240,
      "real_vram_mb": 7450,
      "status": "PASS",
      "reason": "SUCCESS"
    },
    {
      "step": 2,
      "tested_n_ctx": 13312,
      "real_vram_mb": 9850,
      "status": "OOM/FAIL",
      "reason": "CUDA_OOM_EXCEEDED (VRAM usage exceeded 92% threshold)"
    }
  ],
  "peak_vram_mb": 7450,
  "tpot_tok_per_sec": 45.0,
  "is_supported": true,
  "failure_reason": "SUCCESS",
  "stage_status": {
    "Stage 1": "SUCCESS",
    "Stage 2": "SUCCESS",
    "Stage 3": "SUCCESS (Real GPU Load Binary Search)",
    "Stage 4": "SUCCESS"
  }
}
```

---

## 2. Profile Cache File Contract: `config/model_context_profiles.json`

### Storage Permissions
- **File Mode**: `0600` (Owner read/write only)
- **Atomic Operations**: Write to temporary file in `config/` directory -> `os.fsync()` -> Atomic rename (`os.replace()`)

### JSON Schema Structure

```json
{
  "generated_at": "2026-08-07T07:10:00Z",
  "system_hardware": {
    "gpu_name": "NVIDIA GeForce GTX 1080 Ti",
    "total_vram_mb": 11264,
    "is_cuda_available": true
  },
  "profiles": {
    "qwen3.5-2b": {
      "max_context_length": 10240,
      "recommended_context_length": 8192,
      "binary_search_steps": [...],
      "peak_vram_mb": 7450,
      "tpot_tok_per_sec": 45.0,
      "scaling_tested": true,
      "is_supported": true,
      "failure_reason": "SUCCESS",
      "last_tested_at": "2026-08-07T07:10:00Z"
    }
  }
}
```
