# Quickstart & Verification: 044-llm-response-payload-viewer

## Runnable Validation Commands

### 1. Execute Unit & E2E Test Suite
```bash
uv run pytest tests/unit/test_llm_payload_viewer.py -v
```

### 2. Verify REST API Endpoint (`GET /dashboard/api/audit/payload/{id}`)
```bash
curl http://10.0.0.41:8081/dashboard/api/audit/payload/1 -H "X-Admin-Secret": "aiservice"
```

### 3. Verify Google AI Studio Style Dashboard UI
Open `http://10.0.0.41:8081/dashboard/` in browser, navigate to Playground & Audit tabs, and inspect Chat Thread streaming and "View Payload" modal.
