# Data Model & Interface Contracts: 047-think-tag-stripping

## 1. Playground Endpoint Contract (`POST /dashboard/api/playground`)

### Input Request Payload (`PlaygroundRequest`)

```json
{
  "model": "qwen3.5-4b",
  "system_prompt": "You are a helpful AI assistant.",
  "prompt": "Explain black holes",
  "temperature": 0.7,
  "top_p": 0.9,
  "max_tokens": 1024,
  "strip_think_tags": true
}
```

### Output Response Payload (`PlaygroundResponse`)

```json
{
  "text": "A black hole is a region of spacetime where gravity is so strong...",
  "thinking_process": "User is asking about astrophysics. Formulate a simple concise explanation...",
  "ttft_ms": 45.2,
  "total_latency_s": 0.85,
  "token_speed_tok_s": 35.0,
  "prompt_tokens": 15,
  "completion_tokens": 60,
  "finish_reason": "stop"
}
```

## 2. Database Schema (`data/metrics.db`)

```sql
ALTER TABLE api_key_logs ADD COLUMN thinking_text TEXT;
```

- `prompt_text`: Raw user prompt.
- `completion_text`: Cleaned final completion text (without `<think>` tags).
- `thinking_text`: Extracted internal reasoning trace text.
