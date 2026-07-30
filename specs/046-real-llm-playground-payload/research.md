# Research & Technical Choices: 046-real-llm-playground-payload

## 1. Playground Backend LLM Integration
- **Decision**: Replace mock string generation in `run_playground_test` (`src/api/routes/dashboard_api.py`) with `httpx.AsyncClient` posting to `http://127.0.0.1:8089/v1/chat/completions` (or `http://localhost:8089/v1/chat/completions`). Fall back gracefully with clear message if `llama-server` process is offline.
- **Rationale**: Eliminates dummy mock string responses completely from implementation code in compliance with Constitution v1.4.0.

## 2. Reverse Proxy & Playground Payload Capture
- **Decision**: In `src/api/routes/inference_api.py` (reverse proxy route), capture the JSON request body (`messages` / `prompt`) and the LLM JSON response body (`choices[0].message.content`), and call `metrics_db.log_request(..., prompt_text=..., completion_text=...)`.
- **Rationale**: Ensures 100% genuine user prompts and LLM generated completions are persisted into `data/metrics.db` for audit modal inspection.
