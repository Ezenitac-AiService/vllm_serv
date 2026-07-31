# Data Model: SQLite Metrics & Security Specs (043-api-key-auth-toggle)

## Entities

### 1. `api_key_logs` Table (`data/metrics.db`)
```sql
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS api_key_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_key TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    endpoint TEXT NOT NULL,
    status_code INTEGER NOT NULL,
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    ttft_ms REAL DEFAULT 0.0,
    tps REAL DEFAULT 0.0,
    is_error INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_api_key ON api_key_logs(api_key);
CREATE INDEX IF NOT EXISTS idx_timestamp ON api_key_logs(timestamp);
```

### 2. `ServerConfig` Pydantic Entity Update (`config/server_config.json`)
```json
{
  "api_key_enabled": false,
  "api_keys": [
    {
      "key": "sk-vllm-e4f6a...",
      "name": "Production Client",
      "status": "active",
      "created_at": "2026-07-30T15:00:00Z",
      "expires_at": "2026-10-30T15:00:00Z",
      "max_tokens_quota": 1000000,
      "max_rpm_limit": 60
    }
  ]
}
```
