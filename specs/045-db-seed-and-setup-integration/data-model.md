# Data Model: 045-db-seed-and-setup-integration

## Seed Data Entities

### 1. Pre-configured API Key Seeds (`config/server_config.json`)
- `sk-vllm-dev-demo1` (Name: Development Sample Key 1)
- `sk-vllm-mobile-app` (Name: Mobile Application Client)

### 2. Sample Metrics & Payload Seeds (`data/metrics.db`)
- 10 mock inference request logs spanning recent timestamps:
  - 8 successful requests (HTTP 200) with realistic TTFT (30-60ms), TPS (25-45 tok/s), and Prompt/Completion text.
  - 2 error requests (HTTP 401/500) for anomaly testing visualization.
