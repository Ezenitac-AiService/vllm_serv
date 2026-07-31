---

description: "Task list for Legacy Extraction Scripts Local LLM Integration"
---

# Tasks: 레거시 추출 스크립트 자체 서버 LLM 연동 전환 (036-legacy-extraction-llm)

**Input**: Design documents from `/specs/036-legacy-extraction-llm/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included for each user story and must be executed using `uv run pytest`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- File paths are explicitly included in descriptions

## Path Conventions

- **Single project**: `.legacy/`, `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Infrastructure setup and test file shell creation

- [x] T001 Create unit test file shell `tests/unit/test_legacy_extraction_llm.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core endpoint & environment variable resolution helper for local LLM communication

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 Implement local LLM endpoint resolution helper in `.legacy/` and `tests/unit/test_legacy_extraction_llm.py` with priority order: `OPENAI_BASE_URL` > `VLLM_API_BASE` > host LAN IP `10.0.0.41:8000/v1` default (with dynamic active LAN IP fallback) and `OPENAI_API_KEY` > `"EMPTY"`

**Checkpoint**: Foundation ready - local LLM endpoint resolution ready.

---

## Phase 3: User Story 1 - ATEAM 주식 댓글 감성 추출 스크립트 로컬 LLM 연동 (Priority: P1) 🎯 MVP

**Goal**: Remove Groq API calls from `.legacy/ATEAM_ExtractionItem.py` and bind to local server LLM endpoint (`http://10.0.0.41:8000/v1`) with JSON mode fallback and connection error handling.

**Independent Test**: `uv run python .legacy/ATEAM_ExtractionItem.py` & `uv run pytest tests/unit/test_legacy_extraction_llm.py -k test_ateam`

### Tests for User Story 1

- [x] T003 [P] [US1] Write unit tests for `ATEAM_ExtractionItem.py` local LLM client initialization, JSON extraction, and connection error handling in `tests/unit/test_legacy_extraction_llm.py`

### Implementation for User Story 1

- [x] T004 [US1] Update `.legacy/ATEAM_ExtractionItem.py` to remove Groq API (`https://api.groq.com/openai/v1`) and `GROQ_API_KEY`
- [x] T005 [US1] Update `.legacy/ATEAM_ExtractionItem.py` client to use `http://10.0.0.41:8000/v1` (or `OPENAI_BASE_URL`/`VLLM_API_BASE`) and `api_key="EMPTY"`
- [x] T006 [US1] Add connection failure handling and `response_format={"type": "json_object"}` 400 Bad Request fallback (retry without response_format + `<think>` tag stripping + regex JSON parsing) to `process_stock_comment_sentiment_extraction()` in `.legacy/ATEAM_ExtractionItem.py`

**Checkpoint**: At this point, User Story 1 is fully functional and testable independently (MVP ready).

---

## Phase 4: User Story 2 - BTEAM 음식점 리뷰 감성 추출 스크립트 로컬 LLM 연동 (Priority: P2)

**Goal**: Remove Groq API calls from `.legacy/BTEAM_ExtractionItem.py` and bind to local server LLM endpoint (`http://10.0.0.41:8000/v1`) with JSON mode fallback and connection error handling.

**Independent Test**: `uv run python .legacy/BTEAM_ExtractionItem.py` & `uv run pytest tests/unit/test_legacy_extraction_llm.py -k test_bteam`

### Tests for User Story 2

- [x] T007 [P] [US2] Write unit tests for `BTEAM_ExtractionItem.py` local LLM client initialization, JSON extraction, and connection error handling in `tests/unit/test_legacy_extraction_llm.py`

### Implementation for User Story 2

- [x] T008 [US2] Update `.legacy/BTEAM_ExtractionItem.py` to remove Groq API (`https://api.groq.com/openai/v1`) and `GROQ_API_KEY`
- [x] T009 [US2] Update `.legacy/BTEAM_ExtractionItem.py` client to use `http://10.0.0.41:8000/v1` (or `OPENAI_BASE_URL`/`VLLM_API_BASE`) and `api_key="EMPTY"`
- [x] T010 [US2] Add connection failure handling and `response_format={"type": "json_object"}` 400 Bad Request fallback (retry without response_format + `<think>` tag stripping + regex JSON parsing) to `process_review_sentiment_extraction()` in `.legacy/BTEAM_ExtractionItem.py`

**Checkpoint**: User Story 2 adds transparent local LLM extraction to BTEAM review script.

---

## Phase 5: User Story 3 - 환경 변수 구성 및 다중 모델 서빙 라인업 지원 (Priority: P3)

**Goal**: Support multi-model rotation/selection (`gemma4-2b`, `gemma4-4b`, `qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b`) via environment variables in both legacy scripts with automated rotation pytest verification.

**Independent Test**: `OPENAI_MODEL_NAME=gemma4-2b uv run python .legacy/ATEAM_ExtractionItem.py` & `uv run pytest tests/unit/test_legacy_extraction_llm.py -k test_multi_model`

### Tests for User Story 3

- [x] T011 [P] [US3] Write unit tests for multi-model lineup (`gemma4-e2b`, `gemma4-e4b`, `qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b`) rotation loop and environment variable overrides in `tests/unit/test_legacy_extraction_llm.py`

### Implementation for User Story 3

- [x] T012 [US3] Update model name resolution in `.legacy/ATEAM_ExtractionItem.py` to support `gemma4-e2b`, `gemma4-e4b`, `qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b` with priority `OPENAI_MODEL_NAME` > `MODEL_NAME` > `qwen3.5-2b`
- [x] T013 [US3] Update model name resolution in `.legacy/BTEAM_ExtractionItem.py` to support `gemma4-e2b`, `gemma4-e4b`, `qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b` with priority `OPENAI_MODEL_NAME` > `MODEL_NAME` > `qwen3.5-2b`


**Checkpoint**: All user stories (P1, P2, P3) complete with full multi-model test coverage.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and end-to-end suite validation

- [x] T014 [P] Update validation scenarios in `specs/036-legacy-extraction-llm/quickstart.md`
- [x] T015 Run full test suite using `uv run pytest` to ensure zero regressions across existing codebase


---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1) → User Story 2 (P2) → User Story 3 (P3)
- **Polish (Phase 6)**: Depends on all user stories being complete

### Parallel Opportunities

- T003 [P] [US1] and T007 [P] [US2] can run in parallel
- T011 [P] [US3] can run in parallel
- T014 [P] can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational (T002)
3. Complete Phase 3: User Story 1 (T003 - T006)
4. **STOP and VALIDATE**: Run `uv run python .legacy/ATEAM_ExtractionItem.py`
5. MVP Verified!

### Incremental Delivery

1. Setup + Foundational → Local LLM client helper ready
2. Add User Story 1 (P1) → ATEAM stock comment script local LLM integration (MVP!)
3. Add User Story 2 (P2) → BTEAM review script local LLM integration
4. Add User Story 3 (P3) → Multi-model lineup support (`gemma4-2b`, `gemma4-4b`, `qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b`)
5. Polish & full validation (`uv run pytest`)
