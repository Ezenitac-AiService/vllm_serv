# Data Model: start_server.sh 데몬 구동시 PYTHONPATH 예외 및 0.0.0.0 curl 바인딩 오류 수정 (067-fix-server-startup-pythonpath)

**Feature**: `067-fix-server-startup-pythonpath`

## Server Control Lifecycle States

### 1. Daemon Execution Mapping
- **`EXEC_CMD`**: `nohup setsid uv run python -m src.api.server < /dev/null > "$LOG_FILE" 2>&1 &`
- **`PID_FILE`**: `vllm_serv.pid`
- **`LOG_FILE`**: `logs/server.log`

### 2. Curl Healthcheck Target Scheme
- **`SERVER_HOST`**: Configured host string from `server_config.json` (e.g., `"0.0.0.0"`, `"127.0.0.1"`, `"192.168.0.10"`)
- **`CURL_HOST`**:
  - `127.0.0.1` if `SERVER_HOST == "0.0.0.0"`
  - `SERVER_HOST` otherwise

### 3. MetricsDB Lazy Singleton Wrapper Scheme
- **`metrics_db` (Proxy)**: Lazy proxy object that delays `MetricsDB()` instantiation until first attribute access or method call (e.g. `metrics_db.log_request(...)`).
