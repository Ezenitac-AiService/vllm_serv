# Data Model & DTO Specification: 051-fix-model-select-display

## 1. DTO Specifications (`src/api/routes/dashboard_api.py`)

### `CapabilitiesResponse`

| Field | Type | Description |
|---|---|---|
| `platform_profile` | str | Hardware profile |
| `available_models` | List[str] | List of available models (e.g. `["gemma4-e2b", "gemma4-e4b", "gemma4-12b", "qwen3.5-2b", "qwen3.5-4b", "qwen3.5-9b"]`) |
| `current_model` | Optional[str] | Currently loaded model |
| `vram_total` | int | Total VRAM (MB) |
| `limits` | Dict[str, int] | Hardware context limits |
| `api_key_enabled` | bool | Security Mode status |
