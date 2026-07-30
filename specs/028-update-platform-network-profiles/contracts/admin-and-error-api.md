# API Contracts: Admin Benchmark & Context Error Response (028-update-platform-network-profiles)

## Contract 1: Admin On-demand Context Benchmark API

### Endpoint
`POST /v1/admin/benchmark/run`

### Headers
- `Authorization: Bearer <VLLM_ADMIN_SECRET | admin_secret>` (또는 `X-Admin-Secret: <secret>`)
- `Content-Type: application/json`

### Request Body (Optional)
```json
{
  "models": ["gemma4-e2b", "qwen3.5-4b"],
  "force_rebenchmark": true
}
```

### Response Success (200 OK)
```json
{
  "status": "success",
  "message": "Context scaling benchmark completed successfully.",
  "results": {
    "gemma4-e2b": {
      "max_safe_n_ctx": 16384,
      "peak_vram_mb": 4200,
      "status": "SUCCESS"
    },
    "qwen3.5-4b": {
      "max_safe_n_ctx": 8192,
      "peak_vram_mb": 7800,
      "status": "SUCCESS"
    }
  },
  "cached_to": "config/model_context_profiles.json"
}
```

---

## Contract 2: OpenAI-Compatible 400 Bad Request Context Limit Error Response

### Trigger Condition
클라이언트가 `/v1/chat/completions` 또는 `/v1/completions` 요청 시 지정한 `n_ctx` 또는 `prompt_tokens + max_tokens`가 해당 모델/하드웨어 프로필의 `max_n_ctx`를 초과할 경우 발생.

### Response Error (400 Bad Request)
```json
{
  "error": {
    "message": "Requested context length (8192) exceeds model maximum allowed context length (4096) for model 'gemma4-12b'.",
    "type": "invalid_request_error",
    "param": "n_ctx",
    "code": "context_length_exceeded"
  }
}
```
