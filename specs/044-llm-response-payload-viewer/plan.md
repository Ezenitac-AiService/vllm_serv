# Implementation Plan: LLM 프롬프트 및 대답 응답 내용 (Inference Payload) 저장 & Google AI Studio 스타일 대화형 플레이그라운드 고도화 (044-llm-response-payload-viewer)

**Branch**: `044-llm-response-payload-viewer`  
**Specification**: [spec.md](file:///home/dev/storage/vllm_serv/specs/044-llm-response-payload-viewer/spec.md)  
**Research**: [research.md](file:///home/dev/storage/vllm_serv/specs/044-llm-response-payload-viewer/research.md)  
**Data Model**: [data-model.md](file:///home/dev/storage/vllm_serv/specs/044-llm-response-payload-viewer/data-model.md)  

---

## Architecture & Implementation Overview

1. **SQLite Metrics DB Schema Expansion (`src/core/metrics_db.py`)**:
   - `prompt_text` & `completion_text` 컬럼 추가 및 안전한 DB 마이그레이션.
   - `get_payload(request_id)` retrieval 쿼리 핸들러 추가.
2. **Dashboard REST Endpoints (`src/api/routes/dashboard_api.py`)**:
   - `GET /dashboard/api/audit/payload/{request_id}` (Payload Inspector API)
3. **Google AI Studio 2026 Style UI (`src/api/static/index.html` & `app.js`)**:
   - Playground: 2-Column Chat Thread (User / Assistant bubbles) + Side Parameter Panel + SSE Streaming + Metric Chips + Code Export Toolbar.
   - Audit Tab: **[👁️ View Payload (대답 보기)]** 버튼 & 모달 (`payload-modal`).
4. **Verification Test Suite**: `tests/unit/test_llm_payload_viewer.py`

---

## Constitution Compliance Check

- [x] Language: Korean primary for documentation, English for code.
- [x] Anti-Mock Enforcement: Test suite uses real FastAPI TestClient & SQLite execution.
- [x] Non-destructive file edits: Atomic replacement via `replace_file_content`.
- [x] All commands run with `uv run`.
