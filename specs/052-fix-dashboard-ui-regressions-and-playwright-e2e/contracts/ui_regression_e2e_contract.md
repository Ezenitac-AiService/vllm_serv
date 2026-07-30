# Interface Contract: Playwright E2E Dashboard UI Test Suite

## 1. Test Scenarios (`tests/e2e/test_dashboard_ui.py`)

### Scenario 1: Tab Navigation & Dynamic Content Loading
- **Action**: Click `#tab-btn-control`, `#tab-btn-playground`, `#tab-btn-audit`, `#tab-btn-metrics`.
- **Expected Outcome**: Active tab CSS class updates, corresponding panel `#tab-*` becomes visible, page does not refresh.

### Scenario 2: Admin Auth Modal Interaction
- **Action 1**: Click `#admin-login-btn` → Modal `#admin-modal` removes class `hidden`.
- **Action 2**: Click `#modal-close-btn` → Modal `#admin-modal` adds class `hidden`.
- **Action 3**: Click `#admin-login-btn`, fill `#admin-secret-input`, click `#modal-login-btn` → Modal closes, session state updates.

### Scenario 3: Form Submission Reload Prevention
- **Action**: In `#tab-control`, fill `#model-select` or n_ctx and click `#manual-form button[type="submit"]`.
- **Expected Outcome**: Async POST request sent, `e.preventDefault()` halts page reload, active tab remains `control`.
