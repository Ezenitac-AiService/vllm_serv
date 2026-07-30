# Data Model & DTO Specification: 049-playground-model-selection

## 1. DTO Specifications (`src/api/routes/dashboard_api.py`)

### `PlaygroundRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `model` | Optional[str] | No | Target model name selected from `#pg-model-select` |
| `system_prompt` | Optional[str] | No | System prompt instructions |
| `prompt` | str | Yes | User input prompt |
| `temperature` | float | No | Sampling temperature (0.0 - 2.0) |
| `top_p` | float | No | Nucleus sampling top_p (0.0 - 1.0) |
| `max_tokens` | int | No | Maximum output tokens (default: 1024) |
| `session_id` | Optional[str] | No | Chat session UUID |

### `CapabilitiesResponse`

| Field | Type | Description |
|---|---|---|
| `platform_profile` | str | Hardware profile name (e.g. `GPU-80GB-HGX`) |
| `current_model` | str | Currently loaded model on backend server |
| `available_models` | List[str] | List of all available serving models |
