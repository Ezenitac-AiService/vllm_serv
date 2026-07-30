# Data Model & Interface Contracts: 046-real-llm-playground-payload

## Data Pipeline

### 1. `POST /dashboard/api/playground` Payload Contract
- **Input**:
  - `model`: Target LLM model name (e.g. `qwen3.5-4b`)
  - `prompt`: User prompt text
  - `system_instruction`: System instruction prompt
  - `temperature`, `top_p`, `max_tokens`
- **Backend Flow**:
  - Forwards `messages = [{"role": "system", "content": system_instruction}, {"role": "user", "content": prompt}]` to `http://127.0.0.1:8089/v1/chat/completions`.
  - Parses real completion output string from backend response.
  - Logs `prompt_text` & `completion_text` into `data/metrics.db`.
- **Output**:
  ```json
  {
    "status": "success",
    "output": "Real LLM generated text from llama-server...",
    "metrics": {
      "ttft_ms": 42.1,
      "tps": 32.5,
      "total_latency_ms": 850.0,
      "prompt_tokens": 15,
      "completion_tokens": 40
    }
  }
  ```
