# Research & Technical Choices: 050-playground-api-key-auth

## 1. Playground API Key Enforcement Architecture

- **Decision**: Update `GET /dashboard/api/capabilities` to include `api_key_enabled: bool` (from `ConfigManager().get_server_config()`).
- **Decision**: In `src/api/routes/dashboard_api.py`, add `api_key: Optional[str] = None` to `PlaygroundRequest`.
- **Decision**: When `api_key_enabled` is True:
  - Extract API Key from `X-API-Key` header, `Authorization: Bearer <key>` header, or `body.api_key`.
  - Verify key via `ApiKeyManager().verify_key(api_key)` (allowing test fallback keys `sk-vllm-test`, `sk-vllm-dev`).
  - If invalid or missing when `api_key_enabled == True`, reject with HTTP 401 Unauthorized / SSE 401.
- **Rationale**:
  - Prevents security bypass where Playground could invoke C++ LLM backend without authentication even when Security Mode was enabled.
