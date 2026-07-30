# Tasks: API 키 필수 인증 토글, SQLite 메트릭 DB, Enterprise LLM 쿼터 & 비용/성능 모니터링 구현 (043-api-key-auth-toggle)

**Feature Branch**: `043-api-key-auth-toggle`  
**Specification**: [spec.md](file:///home/dev/storage/vllm_serv/specs/043-api-key-auth-toggle/spec.md)  
**Implementation Plan**: [plan.md](file:///home/dev/storage/vllm_serv/specs/043-api-key-auth-toggle/plan.md)  

---

## Phase 1: Setup

- [x] T001 Verify project specification files in `specs/043-api-key-auth-toggle/`

---

## Phase 2: Foundational (Core Infrastructure)

- [x] T002 Implement SQLite WAL metrics database manager module in `src/core/metrics_db.py` managing `data/metrics.db`
- [x] T003 Implement API key authentication & rate limiting middleware in `src/api/middleware/api_key_auth.py`

---

## Phase 3: User Story 1 - API 키 필수/선택 인증 토글 (P1 🎯 MVP)

- [x] T004 [US1] Update `POST /dashboard/api/config` endpoint in `src/api/routes/dashboard_api.py` to toggle `api_key_enabled`
- [x] T005 [US1] Add API Key Enforcement Toggle Switch UI component in `src/api/static/index.html` & `src/api/static/app.js`

---

## Phase 4: User Story 2 - SQLite DB 메트릭 시각화 & Enterprise Observability (P2)

- [x] T006 [P] [US2] Implement metrics aggregation & CSV export endpoints (`GET /dashboard/api/keys/metrics`, `GET /dashboard/api/keys/export/csv`, `POST /dashboard/api/keys/revoke`) in `src/api/routes/dashboard_api.py`
- [x] T007 [P] [US2] Add Top 5 Ranking Chart, Key Metrics Table with Masking (`sk-****-8f3a`), Anomaly Badges (⚠️), Revoke Button & CSV Export UI in `src/api/static/index.html` & `src/api/static/app.js`

---

## Phase 5: Polish & Verification

- [x] T008 Create comprehensive unit/E2E test suite in `tests/unit/test_api_key_auth_toggle.py` and run `uv run pytest tests/unit/test_api_key_auth_toggle.py -v`
