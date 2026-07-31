# Technical Research & Design Decisions: 052-fix-dashboard-ui-regressions-and-playwright-e2e

## 1. DOM Binding Defense Strategy in `src/api/static/app.js`

- **Problem**: When a single property (e.g. `modalCloseBtn`) was missing from the `elements` map, accessing `elements.modalCloseBtn.addEventListener('click', ...)` threw an uncaught `TypeError: Cannot read properties of undefined`. This crashed JS execution midway and prevented subsequent event listeners (modal login, cancel, form submit `e.preventDefault()`, playground buttons) from being attached.
- **Decision**:
  1. Restore missing element definitions: `modalCloseBtn: document.getElementById('modal-close-btn')`.
  2. Guard ALL event listener registrations with Optional Chaining: `elements.modalCloseBtn?.addEventListener('click', ...)`.
  3. Ensure `manualForm?.addEventListener('submit', (e) => { e.preventDefault(); ... })` always calls `e.preventDefault()` on the first line.

## 2. Playwright E2E Test Suite Architecture (`tests/e2e/test_dashboard_ui.py`)

- **Framework Choice**: `pytest-playwright` / `playwright` with Python `TestClient` or background server fixture.
- **Coverage Scenarios**:
  1. Tab Switching: Live Metrics, Model & Config, AI Playground, Audit & API Keys.
  2. Admin Auth Modal: Open, Close via Cancel button, Authenticate via Secret Key.
  3. Form Submission: Submit `manual-form` and verify no page reload occurs (tab remains `control`).
  4. Playground: Send prompt and verify response text stream.
