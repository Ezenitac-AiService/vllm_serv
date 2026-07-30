# Research & Technical Choices: 049-playground-model-selection

## 1. Dynamic Model Dropdown & Server Onload Model Auto-Sync

- **Decision**: Update `src/api/static/index.html` to add `<select id="pg-model-select">` and update `src/api/static/app.js` to populate `#pg-model-select` options from `caps.available_models` and set `#pg-model-select.value = caps.current_model` during `GET /dashboard/api/capabilities` load.
- **Rationale**:
  - Automatically syncs the Playground default model with the server's actively loaded model upon page load or configuration change (`applyPreset` / `unload`).
  - Eliminates hardcoded model strings (`qwen3.5-4b` defaults when another model is serving).

## 2. SSE Metrics Parsing Bug Fix (`JSON.parse`)

- **Decision**: In `src/api/static/app.js`, fix the SSE parser where `JSON.loads` (Python syntax) was erroneously called instead of `JSON.parse(dataStr)`.
- **Rationale**:
  - Resolves the issue where TTFT(ms), Latency(s), and Prompt/Completion token counts were failing to render on the dashboard cards.
