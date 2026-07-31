# Technical Research & Root Cause Fix Choices: 051-fix-model-select-display

## 1. Root Cause Fix in `ConfigManager`

- **Issue**: `_model_catalog_cache: Optional[Dict[str, Any]] = None` in `src/core/config_manager.py` gets sticky-set to `{}` if any read error occurs, causing all subsequent `get_model_catalog()` calls to return `{}`.
- **Fix**:
  1. In `get_model_catalog()`, if `_model_catalog_cache` is `{}` or `None`, attempt to re-read `model_catalog.json`.
  2. If file reading fails, fallback to hardcoded default dictionary of official 6 models (`gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`, `qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b`) instead of caching empty `{}`.

## 2. Frontend Options Population Fix

- **Issue**: In `app.js`, `loadCapabilities()` populates `#model-select` and `#pg-model-select`.
- **Fix**: Ensure options are populated with catalog model keys and `selected = true` is set for `caps.current_model`.
