# Tasks: 실할당 LAN IP 접속 및 Playwright E2E 브라우저 실측 검증 (042-e2e-playwright-real-ip-firewall-verification)

**Input**: Design documents from `/specs/042-e2e-playwright-real-ip-firewall-verification/`

---

## Phase 1: Setup

- [x] T001 Verify project specification files in `specs/042-e2e-playwright-real-ip-firewall-verification/`

---

## Phase 2: Foundational & Core Implementation

- [x] T002 Verify and enforce `0.0.0.0` host binding in `src/core/config_manager.py` & `src/api/server.py`
- [x] T003 Update `scripts/start_server.sh` to automatically spawn both port 8081 LLM API and port 8089 Dashboard API with `0.0.0.0` binding
- [x] T004 Update `scripts/benchmark_quality.py` `finally` block to verify and auto-restore port 8089 Dashboard API process

---

## Phase 3: Playwright E2E Browser Testing (US1 🎯 MVP)

- [x] T005 Create Playwright E2E browser test suite in `tests/e2e/test_dashboard_playwright_real.py` connecting to `http://10.0.0.41:8089/dashboard`
- [x] T006 Verify HTTP 200 response, DOM rendering (title, health status cards), and screenshot capture via Playwright

---

## Phase 4: Polish & Verification

- [x] T007 Execute full test suite `uv run pytest tests/e2e/test_dashboard_playwright_real.py`
