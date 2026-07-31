# Quickstart & Validation Guide: 050-playground-api-key-auth

## Validation Commands & Verification Status

### 1. Run Unit Test Suite for Playground API Key Authentication
```bash
uv run pytest tests/unit/test_playground_api_key_auth.py -v
```
**Status**: ✅ PASSED (2/2 tests passed)

### 2. Run Full Regression Suite
```bash
uv run pytest tests/unit/test_playground_api_key_auth.py tests/unit/test_playground_model_selection.py tests/unit/test_think_tag_ui_markdown.py tests/unit/test_think_tag_stripping.py tests/unit/test_real_llm_playground_payload.py tests/unit/test_llm_payload_viewer.py -v
```
**Status**: ✅ PASSED (16/16 tests passed, 100% green)

## UI & Security Feature Verification
- [x] `api_key_enabled: bool` returned in `GET /dashboard/api/capabilities`
- [x] `#pg-api-key` input added to Playground Settings Panel in `index.html`
- [x] Dynamic label badge updated based on Security Mode (`Required in Security Mode` / `Optional`) in `app.js`
- [x] 401 Unauthorized rejection when Security Mode is ON without valid API key
- [x] Valid API Key passed in `X-API-Key` header / `api_key` payload and logged in `metrics_db`
