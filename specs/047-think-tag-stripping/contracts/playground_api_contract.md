# Interface Contract: Playground & Proxy Think-Tag Stripping API

## 1. `POST /dashboard/api/playground`

- **Content-Type**: `application/json`
- **Request Parameters**:
  - `model` (string, optional): Target LLM model ID.
  - `system_prompt` (string, optional): System prompt instruction.
  - `prompt` (string, required): User prompt text.
  - `temperature` (float, default `0.7`): Sampling temperature.
  - `top_p` (float, default `0.9`): Top-p nucleus sampling.
  - `max_tokens` (integer, default `1024`): Maximum token generation limit.
  - `strip_think_tags` (boolean, default `true`): Enable `<think>` tag stripping.

- **Response Body**:
  - `text` (string): Cleaned final completion text.
  - `thinking_process` (string or null): Extracted internal reasoning trace text.
  - `ttft_ms` (float): Time to first token in milliseconds.
  - `total_latency_s` (float): Total request latency in seconds.
  - `token_speed_tok_s` (float): Token generation speed (tok/s).
  - `prompt_tokens` (integer): Input prompt token count.
  - `completion_tokens` (integer): Output token count.
  - `finish_reason` (string): Completion status (`stop`, `length`, `offline`, `error`).
