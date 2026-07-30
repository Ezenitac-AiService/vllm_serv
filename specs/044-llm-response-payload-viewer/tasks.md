# Tasks: LLM 프롬프트 및 대답 응답 내용 (Inference Payload) 저장 & Google AI Studio 스타일 대화형 플레이그라운드 고도화 (044-llm-response-payload-viewer)

**Feature**: `044-llm-response-payload-viewer`  
**Specification**: [spec.md](file:///home/dev/storage/vllm_serv/specs/044-llm-response-payload-viewer/spec.md)  
**Implementation Plan**: [plan.md](file:///home/dev/storage/vllm_serv/specs/044-llm-response-payload-viewer/plan.md)  

---

## Phase 1: Setup

- [x] T001 Verify project specification & planning files in `specs/044-llm-response-payload-viewer/`

---

## Phase 2: Foundational (Core Infrastructure)

- [x] T002 Update SQLite WAL metrics database schema in `src/core/metrics_db.py` adding `prompt_text` and `completion_text` columns & `get_payload_by_id()` query handler

---

## Phase 3: User Story 1 - Google AI Studio 2026 Style 대화형 플레이그라운드 UI/UX 고도화 (P1 🎯 MVP)

- [x] T003 [US1] Redesign AI Playground HTML layout in `src/api/static/index.html` to 2-Column Chat Thread (User / Assistant bubbles) + Side Parameter Panel
- [x] T004 [US1] Implement SSE (Server-Sent Events) token streaming animation, Metric Chips (TTFT ms, Tok/s, Cost) & Code Export Toolbar in `src/api/static/app.js` and `src/api/static/style.css`

---

## Phase 4: User Story 2 - Audit 로그 대답 원문 Payload Inspector 팝업 모달 & REST API (P2)

- [x] T005 [P] [US2] Implement REST API endpoint `GET /dashboard/api/audit/payload/{log_id}` in `src/api/routes/dashboard_api.py`
- [x] T006 [P] [US2] Add **[👁️ View Payload]** button row & `payload-modal` popup inspector UI in `src/api/static/index.html` & `src/api/static/app.js`

---

## Phase 5: Polish & Verification

- [x] T007 Create comprehensive unit & integration test suite in `tests/unit/test_llm_payload_viewer.py` and run `uv run pytest tests/unit/test_llm_payload_viewer.py -v`
