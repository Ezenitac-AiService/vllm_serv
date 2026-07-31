# Interface Contract: Capabilities & Model Selection API

## 1. `GET /dashboard/api/capabilities`
- **Response Status**: 200 OK
- **Response Schema**:
  ```json
  {
    "platform_profile": "Platform_A_Development",
    "vram_total": 24000,
    "available_models": [
      "gemma4-e2b",
      "gemma4-e4b",
      "gemma4-12b",
      "qwen3.5-2b",
      "qwen3.5-4b",
      "qwen3.5-9b"
    ],
    "limits": {
      "gemma4-e2b": 35000,
      "gemma4-e4b": 16000,
      "gemma4-12b": 9500,
      "qwen3.5-2b": 32000,
      "qwen3.5-4b": 18000,
      "qwen3.5-9b": 8500
    },
    "current_model": "qwen3.5-4b",
    "current_n_ctx": 4096,
    "api_key_enabled": false
  }
  ```
