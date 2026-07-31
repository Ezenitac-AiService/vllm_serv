# Data Model & DTO Specification: 050-playground-api-key-auth

## 1. DTO Specifications (`src/api/routes/dashboard_api.py`)

### `PlaygroundRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `api_key` | Optional[str] | No | API Key string (`sk-vllm-...`) provided by user in Playground |
| `model` | Optional[str] | No | Target model name |
| `system_prompt` | Optional[str] | No | System instructions |
| `prompt` | str | Yes | User input prompt |
| `temperature` | float | No | Temperature |
| `top_p` | float | No | Top_p |
| `max_tokens` | int | No | Max output tokens |
| `session_id` | Optional[str] | No | Chat session UUID |

### `CapabilitiesResponse`

| Field | Type | Description |
|---|---|---|
| `platform_profile` | str | Hardware profile |
| `current_model` | str | Currently loaded model |
| `available_models` | List[str] | List of available models |
| `api_key_enabled` | bool | Security Mode status (True = Required, False = Public) |
