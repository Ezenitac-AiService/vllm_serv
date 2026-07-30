# Data Model & UI Element Contract: 052-fix-dashboard-ui-regressions-and-playwright-e2e

## 1. UI DOM Element Map (`src/api/static/app.js`)

| Element ID | Purpose | Required Event | Guard Requirement |
|---|---|---|---|
| `admin-login-btn` | Open admin modal | `click` | `elements.adminLoginBtn?.addEventListener` |
| `admin-modal` | Admin modal container | CSS toggle `hidden` | `elements.adminModal` |
| `modal-close-btn` | Close admin modal (Cancel) | `click` | `elements.modalCloseBtn?.addEventListener` |
| `modal-login-btn` | Submit admin secret key | `click` | `elements.modalLoginBtn?.addEventListener` |
| `manual-form` | Server configuration form | `submit` | `elements.manualForm?.addEventListener('submit', (e) => e.preventDefault())` |
| `tab-*` | Navigation tabs | `click` | `elements.tabs.forEach(...)` |
