# Contract: Model Catalog Schema & Serving Parameters

## 1. Catalog JSON Contract (`config/model_catalog.json`)

`qwen3.5-9b-vision` 신규 엔트리의 정확한 JSON 표현 계약입니다.

```json
{
  "qwen3.5-9b-vision": {
    "name": "Qwen 3.5 9B Vision",
    "repo_id": "unsloth/Qwen3.5-9B-GGUF",
    "filename": "Qwen3.5-9B-Q4_K_M.gguf",
    "clip_filename": "mmproj-BF16.gguf",
    "target_dir": "models/qwen3.5-9b-vision",
    "model_path": "models/qwen3.5-9b-vision/Qwen3.5-9B-Q4_K_M.gguf",
    "clip_path": "models/qwen3.5-9b-vision/mmproj-BF16.gguf",
    "chat_template": "chatml",
    "default_n_ctx": 4096,
    "vram_est_mb": 9800,
    "requires_mmproj": true,
    "quant_type": "q4_k_m",
    "size_gb": 5.8,
    "n_layers": 40,
    "n_heads": 32,
    "n_head_kv": 8,
    "head_dim": 128,
    "max_n_ctx": 131072
  }
}
```

---

## 2. Server CLI Invocation Contract (`llama-server`)

`qwen3.5-9b-vision` 모델이 선택되었을 때 구동 스크립트(`scripts/start_server.sh`)가 바인딩해야 하는 명령행 파라미터 규격입니다.

```bash
llama-server \
  --model models/qwen3.5-9b-vision/Qwen3.5-9B-Q4_K_M.gguf \
  --mmproj models/qwen3.5-9b-vision/mmproj-BF16.gguf \
  --ctx-size 4096 \
  --port 8080
```
