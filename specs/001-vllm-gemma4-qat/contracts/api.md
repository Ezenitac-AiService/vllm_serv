# API Contracts

## 1. Text Generation API (OpenAI Compatible)
**Endpoint**: `POST /v1/chat/completions`

**Request Body**:
```json
{
  "model": "gemma4-current",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "max_tokens": 100,
  "temperature": 0.7
}
```

**Response Body**:
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "gemma4-current",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Hi there!"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 9,
    "completion_tokens": 12,
    "total_tokens": 21
  }
}
```

## 2. Model Switch API (Dynamic Loading)
**Endpoint**: `POST /api/models/switch`

**Request Body**:
```json
{
  "model_id": "gemma4-4b"
}
```

**Response Body**:
```json
{
  "status": "success",
  "message": "Model switched to gemma4-4b",
  "load_time_sec": 4.5
}
```
