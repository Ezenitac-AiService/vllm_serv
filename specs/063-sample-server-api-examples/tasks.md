# Tasks: vllm_serv API 예제 샘플 스크립트 작성 (sample_01 ~ sample_05)

**Input**: Design documents from `/specs/063-sample-server-api-examples/`

**Prerequisites**: [plan.md](file:///home/dev/storage/vllm_serv/specs/063-sample-server-api-examples/plan.md), [spec.md](file:///home/dev/storage/vllm_serv/specs/063-sample-server-api-examples/spec.md), [research.md](file:///home/dev/storage/vllm_serv/specs/063-sample-server-api-examples/research.md), [data-model.md](file:///home/dev/storage/vllm_serv/specs/063-sample-server-api-examples/data-model.md), [quickstart.md](file:///home/dev/storage/vllm_serv/specs/063-sample-server-api-examples/quickstart.md)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and sample directory structure

- [x] T001 Verify `samples/` directory structure and `pyproject.toml` dependencies (`httpx`, `pydantic`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Common helper and error handling functions for server connection validation

- [x] T002 [P] Create common helper module with Korean connection error guidance in `samples/common.py`

**Checkpoint**: Foundation ready - user story implementation can begin in parallel

---

## Phase 3: User Story 1 - 독립 실행 가능한 일반 채팅 호출 예제 (`sample_01_chat.py`) (Priority: P1) 🎯 MVP

**Goal**: Enable standard OpenAI-compatible `/v1/chat/completions` LLM chat completion API call example on port 8081.

**Independent Test**: Run `uv run python samples/sample_01_chat.py` and verify HTTP 200 OK and model answer text output.

### Tests for User Story 1 ⚠️

- [x] T003 [P] [US1] Write unit test for `sample_01_chat.py` in `tests/unit/test_sample_scripts.py`

### Implementation for User Story 1

- [x] T004 [US1] Create standard chat completions sample script in `samples/sample_01_chat.py` (port 8081 `/v1/chat/completions`)

**Checkpoint**: User Story 1 fully functional — basic LLM chat API call verified.

---

## Phase 4: User Story 2 - 동적 모델 변경 및 추론 파라미터 제어 예제 (`sample_02_model_params.py`) (Priority: P2)

**Goal**: Demonstrate dynamic model switching and parameter tuning (`temperature`, `top_p`, `max_tokens`, `stop`).

**Independent Test**: Run `uv run python samples/sample_02_model_params.py` and verify multi-parameter responses.

### Tests for User Story 2 ⚠️

- [x] T005 [P] [US2] Write unit test for `sample_02_model_params.py` in `tests/unit/test_sample_scripts.py`

### Implementation for User Story 2

- [x] T006 [US2] Create dynamic model and parameter control sample script in `samples/sample_02_model_params.py`

**Checkpoint**: User Story 2 fully functional — parameter control verified.

---

## Phase 5: User Story 3 - 임베딩 및 리랭킹 보조 모델 전용 호출 예제 (`sample_03_embedding.py`, `sample_04_reranking.py`) (Priority: P3)

**Goal**: Demonstrate BGE M3 embedding model (port 8090) and BGE Reranker v2 M3 model (port 8091) API calls.

**Independent Test**: Run `uv run python samples/sample_03_embedding.py` and `uv run python samples/sample_04_reranking.py` and verify 1024-dim vector outputs and relevance scores.

### Tests for User Story 3 ⚠️

- [x] T007 [P] [US3] Write unit test for embedding and reranking sample scripts in `tests/unit/test_sample_scripts.py`

### Implementation for User Story 3

- [x] T008 [P] [US3] Create BGE M3 embedding sample script in `samples/sample_03_embedding.py` (port 8090 `/v1/embeddings`)
- [x] T009 [US3] Create BGE Reranker v2 M3 sample script in `samples/sample_04_reranking.py` (port 8091 `/v1/embeddings` & `/rerank`)

**Checkpoint**: User Story 3 fully functional — auxiliary embedding and reranking API calls verified.

---

## Phase 6: User Story 4 - Pydantic 기반 구조화된 출력 규격 추출 예제 (`sample_05_structured_output.py`) (Priority: P4)

**Goal**: Demonstrate JSON Schema prompt injection and Pydantic validation using `.legacy/ATEAM_ExtractionItem.py` & `.legacy/BTEAM_ExtractionItem.py` schemas.

**Independent Test**: Run `uv run python samples/sample_05_structured_output.py` and verify ATEAM/BTEAM Pydantic instance parsing.

### Tests for User Story 4 ⚠️

- [x] T010 [P] [US4] Write unit test for `sample_05_structured_output.py` in `tests/unit/test_sample_scripts.py`

### Implementation for User Story 4

- [x] T011 [US4] Create structured output extraction sample script in `samples/sample_05_structured_output.py` importing ATEAM/BTEAM schemas from `.legacy/`

**Checkpoint**: User Story 4 fully functional — Pydantic schema-driven structured output parsing verified.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Quickstart validation and full regression test suite execution

- [x] T012 Run quickstart validation scenarios documented in `quickstart.md`
- [x] T013 Run full regression test suite (`uv run pytest`) to ensure 100% Green Pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1) → User Story 2 (P2) → User Story 3 (P3) → User Story 4 (P4)
- **Polish (Phase 7)**: Depends on all user stories being complete

### Parallel Opportunities

- T003, T005, T007, T008, T010 can run in parallel (different files, no dependencies)
- Implementation tasks follow TDD order: test written → code implemented → test verified

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup (Phase 1) and Foundational (Phase 2)
2. Complete User Story 1 (Phase 3)
3. Validate basic chat API call independently (`uv run python samples/sample_01_chat.py`)

### Incremental Delivery

1. Deliver MVP (`sample_01_chat.py`)
2. Add User Story 2 (`sample_02_model_params.py`)
3. Add User Story 3 (`sample_03_embedding.py`, `sample_04_reranking.py`)
4. Add User Story 4 (`sample_05_structured_output.py`)
5. Execute full regression suite & quickstart validation
