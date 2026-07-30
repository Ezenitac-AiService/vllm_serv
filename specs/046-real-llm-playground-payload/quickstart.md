# Quickstart & Verification: 046-real-llm-playground-payload

## Validation Commands

### 1. Run Real Execution Test Suite
```bash
uv run pytest tests/unit/test_real_llm_playground_payload.py -v
```

### 2. Verify Full Unit Test Suite Regression
```bash
uv run pytest tests/unit/test_api_key_auth_toggle.py tests/unit/test_llm_payload_viewer.py tests/unit/test_db_seed_integration.py tests/unit/test_real_llm_playground_payload.py -v
```
