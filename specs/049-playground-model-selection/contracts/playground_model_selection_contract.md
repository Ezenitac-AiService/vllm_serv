# Interface Contract: Playground Model Selection & Capabilities API

## 1. `GET /dashboard/api/capabilities`
- **Response**:
  ```json
  {
    "platform_profile": "GPU-80GB-HGX",
    "vram_total": 81920,
    "current_model": "deepseek-r1-qwen3.5-7b",
    "available_models": [
      "deepseek-r1-qwen3.5-7b",
      "qwen3.5-4b",
      "llama-3-8b-instruct"
    ]
  }
  ```

## 2. `POST /dashboard/api/playground/stream`
- **Request Body**:
  ```json
  {
    "model": "deepseek-r1-qwen3.5-7b",
    "prompt": "Hello world",
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 1024
  }
  ```
