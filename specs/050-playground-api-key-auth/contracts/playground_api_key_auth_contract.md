# Interface Contract: Playground API Key Authentication API

## 1. `GET /dashboard/api/capabilities`
- **Response**:
  ```json
  {
    "platform_profile": "GPU-80GB-HGX",
    "current_model": "deepseek-r1-qwen3.5-7b",
    "available_models": ["deepseek-r1-qwen3.5-7b", "qwen3.5-4b"],
    "api_key_enabled": true
  }
  ```

## 2. `POST /dashboard/api/playground/stream` (401 Error Response when `api_key_enabled == true` and key is invalid)
- **HTTP Status**: 401 Unauthorized
- **Response Body**:
  ```json
  {
    "detail": "API Key authentication required. Security Mode is enabled."
  }
  ```
