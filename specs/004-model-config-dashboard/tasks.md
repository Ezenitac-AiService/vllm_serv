# Implementation Tasks: 모델 설정 웹 대시보드

**Feature**: 004-model-config-dashboard
**Spec**: [spec.md](spec.md)

## Phase 1: Setup

- [x] T001 Create dashboard static directory `src/api/static` and touch `index.html`, `style.css`, `app.js`
- [x] T002 Update `src/api/main.py` to mount `/dashboard` pointing to `src/api/static`

## Phase 2: Foundational

- [x] T003 Implement `ConfigManager` in `src/core/config_manager.py` to read/write `config/model_config.json`
- [x] T003a [P] Write unit tests for `ConfigManager` in `tests/unit/test_config_manager.py`
- [x] T004 Implement 503 Maintenance Middleware and Reverse Proxy in `src/api/routes/inference_api.py` to intercept `/v1` requests based on `LlamaManager` status, forwarding valid requests to the `llama-server` subprocess using `httpx`.

## Phase 3: User Story 1 (벤치마크 기반 빠른 프리셋 적용)

- [x] T005 [US1] Update `src/core/llama_manager.py` to track `state` and dispatch internal SSE events. **CRITICAL**: Use `subprocess.Popen` to manage the `llama-server` binary process (Subprocess Proxy Architecture) for true continuous batching and OOM isolation.
- [x] T006 [US1] Create REST API endpoints in `src/api/routes/dashboard_api.py` for fetching config and applying presets
- [x] T006a [US1] Write integration tests in `tests/integration/test_dashboard_api.py` to verify successful model swap and preset application
- [x] T007 [P] [US1] Build Preset UI buttons in `src/api/static/index.html` and logic in `src/api/static/app.js`

## Phase 4: User Story 2 (상세 설정 조정 창)

- [x] T008 [US2] Implement hardware limits logic in `LlamaManager` and expose `/capabilities` API in `src/api/routes/dashboard_api.py`
- [x] T008a [P] [US2] Write unit tests for hardware limits logic in `tests/unit/test_llama_manager.py`
- [x] T009 [P] [US2] Build Manual Setting form (Model Selection & Context Slider) in `src/api/static/index.html`
- [x] T010 [P] [US2] Add client-side validation logic in `app.js` using fetched `/capabilities` to show OOM warning

## Phase 5: User Story 3 (서버 모델 실시간 리로드 적용)

- [x] T011 [US3] Create `/stream` endpoint in `dashboard_api.py` using FastAPI `EventSourceResponse` mapping to `LlamaManager` events (Handle `DASHBOARD_TOKEN` auth via Query Parameter since `EventSource` lacks header support)
- [x] T012 [P] [US3] Add loading state/progress UI components in `src/api/static/index.html`
- [x] T013 [P] [US3] Implement `EventSource` subscriber in `app.js` to update loading state dynamically

## Phase 6: User Story 4 (수동 모델 제어 및 503 방어)

- [x] T014 [US4] Add `unload_model()` function to `LlamaManager` and `/unload` endpoint to `dashboard_api.py`
- [x] T015 [P] [US4] Add Unload button in `index.html` and connect in `app.js`
- [x] T016 [US4] Write integration tests in `tests/integration/test_dashboard.py` to assert 503 errors during unload/loading

## Phase 7: Polish & Cross-Cutting Concerns

- [x] T017 [P] Implement basic API Token verification reading `DASHBOARD_TOKEN` env var in `dashboard_api.py`
- [x] T018 [P] Apply modern Glassmorphism styling and animations in `src/api/static/style.css`

## Phase 8: Convergence

- [x] T019 Implement FastAPI lifespan in `src/api/main.py` to automatically load the last configured model on startup per FR-008 (missing)
- [x] T020 Add `asyncio.Lock` to `LlamaManager.load_model` in `src/core/llama_manager.py` to prevent race conditions on rapid concurrent preset requests per Edge Cases (partial)
