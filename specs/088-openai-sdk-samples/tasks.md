# Tasks: OpenAI API 및 httpx 1:1 대칭 실습 예제 수트 작성 (`sample_01`~`06` & `openai_01`~`06` 총 12종) 및 `uv` 재현 환경 구성

**Input**: Design documents from `/specs/088-openai-sdk-samples/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 프로젝트 초기화 및 동적 설정 기반 구축

- [X] T001 Initialize/verify dynamic configuration structure in `samples/config.json`
- [X] T002 [P] Create default configuration template in `samples/config.json.example`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 12개 실습 예제 스크립트 공통 기반 유틸리티 및 `uv` 패키지 관리 체계 구축

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Update `samples/common.py` to support dynamic host/port/model loading from `samples/config.json` and `.env` with fallback
- [X] T004 [P] Configure `pyproject.toml` dependencies (`openai>=1.0.0`, `httpx>=0.27.0`, `pydantic>=2.0.0`, `pytest>=8.0.0`) in `pyproject.toml`
- [X] T005 [P] Generate `uv.lock` lockfile and verify `.venv` exclusion in `.gitignore`
- [X] T006 [P] Create unit test framework for sample scripts in `tests/unit/test_samples.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - OpenAI SDK 대화 및 파라미터 제어 1:1 대칭 실습 예제 (Priority: P1) 🎯 MVP

**Goal**: `sample_01_chat.py` / `openai_01_chat.py` 및 `sample_02_model_params.py` / `openai_02_model_params.py` 1:1 대칭 구축

**Independent Test**: `uv run python samples/sample_01_chat.py` 및 `uv run python samples/openai_01_chat.py` 단독 실행 검증

### Tests for User Story 1

- [X] T007 [P] [US1] Create unit test for chat completion endpoints in `tests/unit/test_chat_samples.py`

### Implementation for User Story 1

- [X] T008 [P] [US1] Refactor `sample_01_chat.py` to use dynamic config from `common.py` in `samples/sample_01_chat.py`
- [X] T009 [US1] Implement `openai_01_chat.py` using `OpenAI` client and `<think>` tag stripping in `samples/openai_01_chat.py`
- [X] T010 [P] [US1] Refactor `sample_02_model_params.py` to use dynamic config in `samples/sample_02_model_params.py`
- [X] T011 [US1] Implement `openai_02_model_params.py` using `OpenAI` client with `temperature=0.0` and `stop=["\n"]` in `samples/openai_02_model_params.py`

**Checkpoint**: User Story 1 (Chat & Parameters) fully functional and testable independently

---

## Phase 4: User Story 2 - 단일 및 배치(Batch) 텍스트 임베딩 수치 벡터 추출 1:1 대칭 예제 (Priority: P2)

**Goal**: `sample_03_embedding.py` 및 `openai_03_embedding.py` 단일 & 배치(Batch) 1024차원 수치 벡터 추출 구축

**Independent Test**: `uv run python samples/sample_03_embedding.py` 및 `uv run python samples/openai_03_embedding.py` 단독 실행 검증

### Tests for User Story 2

- [X] T012 [P] [US2] Create unit test for single & batch embedding extraction in `tests/unit/test_embedding_samples.py`

### Implementation for User Story 2

- [X] T013 [P] [US2] Update `sample_03_embedding.py` to demonstrate batch text list embedding in `samples/sample_03_embedding.py`
- [X] T014 [US2] Implement `openai_03_embedding.py` using `client.embeddings.create()` for single & batch inputs in `samples/openai_03_embedding.py`

**Checkpoint**: User Story 2 (Embedding Single & Batch) fully functional and testable independently

---

## Phase 5: User Story 3 - Reranker 및 단일/배치 Pydantic 구조화 응답 1:1 대칭 예제 (Priority: P3)

**Goal**: `sample_04`, `sample_05`, `sample_06` 및 `openai_04`, `openai_05`, `openai_06` 1:1 대칭 구축

**Independent Test**: `uv run python samples/sample_06_structured_output_batch.py` 및 `uv run python samples/openai_06_structured_output_batch.py` 실행 검증

### Tests for User Story 3

- [X] T015 [P] [US3] Create unit test for reranking and structured output batch in `tests/unit/test_rerank_structured_samples.py`

### Implementation for User Story 3

- [X] T016 [P] [US3] Refactor `sample_04_reranking.py` to use dynamic config in `samples/sample_04_reranking.py`
- [X] T017 [US3] Implement `openai_04_reranking.py` using `OpenAI` client requests in `samples/openai_04_reranking.py`
- [X] T018 [P] [US3] Refactor `sample_05_structured_output.py` to use dynamic config in `samples/sample_05_structured_output.py`
- [X] T019 [US3] Implement `openai_05_structured_output.py` using `OpenAI` client and Pydantic validation in `samples/openai_05_structured_output.py`
- [X] T020 [P] [US3] Implement `sample_06_structured_output_batch.py` (httpx batch structured output) in `samples/sample_06_structured_output_batch.py`
- [X] T021 [US3] Implement `openai_06_structured_output_batch.py` (OpenAI SDK batch structured output) in `samples/openai_06_structured_output_batch.py`

**Checkpoint**: User Story 3 (Reranker & Single/Batch Structured Output) fully functional

---

## Phase 6: User Story 4 - 훈련생 `uv sync` 가상환경 즉시 복원 및 배포 환경 검증 (Priority: P1)

**Goal**: `.venv` 폴더 없이 `uv sync` 명령어로 100% 가상환경 원복 보장

**Independent Test**: `.venv` 삭제 후 `uv sync` 및 `uv run python -c "import openai, httpx, pydantic"` 실행 검증

### Implementation for User Story 4

- [X] T022 [P] [US4] Verify `.venv` is listed in `.gitignore` and build scripts in `.gitignore`
- [X] T023 [US4] Test clean environment recovery by removing `.venv` and executing `uv sync` in repo root

**Checkpoint**: User Story 4 (uv sync environment recovery) verified

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: 문맥 통합 가이드 작성 및 전체 회귀 테스트 검증

- [X] T024 [P] Update `samples/README.md` with 12 paired scripts guide and `uv sync` recovery instructions in `samples/README.md`
- [X] T025 Run quickstart validation guide and full test suite via `uv run pytest tests/unit/test_samples.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1) → MVP
  - User Story 4 (P1) → Environment setup verification
  - User Story 2 (P2) → Embedding single & batch
  - User Story 3 (P3) → Rerank & structured output single & batch
- **Polish (Phase 7)**: Depends on all user stories completion

### Parallel Opportunities

- T002, T004, T005, T006 can run in parallel (Phase 1 & Phase 2 setup)
- T007, T008, T010 can run in parallel (US1)
- T012, T013 can run in parallel (US2)
- T015, T016, T018, T020 can run in parallel (US3)
- T022 can run in parallel (US4)
- T024 can run in parallel (Polish)

---

## Parallel Example: User Story 1 & 2

```bash
# Launch parallel model/test creations:
Task T007: "Create unit test for chat completion endpoints in tests/unit/test_chat_samples.py"
Task T008: "Refactor sample_01_chat.py to use dynamic config from common.py in samples/sample_01_chat.py"
Task T010: "Refactor sample_02_model_params.py to use dynamic config in samples/sample_02_model_params.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 & 4)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (`openai_01`, `openai_02` & `sample_01`, `sample_02`)
4. Complete Phase 6: User Story 4 (`uv sync` environment validation)
5. **STOP and VALIDATE**: Test User Story 1 & 4 independently (MVP ready!)

### Incremental Delivery

1. Add User Story 2 (`openai_03` & `sample_03` single/batch embedding)
2. Add User Story 3 (`openai_04`, `openai_05`, `openai_06` & `sample_04`, `sample_05`, `sample_06`)
3. Complete Phase 7: Polish & Documentation (`samples/README.md`)
