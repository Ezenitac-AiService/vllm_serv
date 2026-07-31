# Data Model: 044-llm-response-payload-viewer

## Database Table: `api_key_logs` (SQLite `data/metrics.db`)

| Column Name | Type | Constraints | Description |
|-------------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique log record ID |
| `api_key` | TEXT | NOT NULL | Masked or raw API key identifier |
| `endpoint` | TEXT | NOT NULL | API route (e.g. `/v1/chat/completions`) |
| `status_code` | INTEGER | NOT NULL | HTTP status code |
| `prompt_tokens` | INTEGER | DEFAULT 0 | Input prompt token count |
| `completion_tokens` | INTEGER | DEFAULT 0 | Output completion token count |
| `process_time_ms` | REAL | DEFAULT 0.0 | Request latency in milliseconds |
| `prompt_text` | TEXT | NULLABLE | Input prompt text content |
| `completion_text` | TEXT | NULLABLE | LLM response completion text content |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | ISO8601 creation timestamp |
