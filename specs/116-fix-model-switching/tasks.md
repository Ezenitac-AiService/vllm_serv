# Tasks: 동적 모델 스위칭(Model Switching) 정상화 및 샘플 연동 개선

**Input**: Design documents from `/specs/116-fix-model-switching/`  
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/  

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Includes exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and prerequisite test verification

- [x] T001 Verify project structure and inspect existing proxy tests in `tests/unit/test_inference_api_proxy_headers.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core LlamaManager lock and hot-swap synchronization prerequisites

- [x] T002 Ensure `LlamaManager` lock mechanism and state tracking in `src/core/llama_manager.py` for safe concurrent hot-swap operations

---

## Phase 3: User Story 1 - POST /v1/chat/completions 자동 모델 핫스왑 지원 (Priority: P1) 🎯 MVP

**Goal**: `POST /v1/chat/completions` 요청 시 payload의 `model` 인자가 현재 VRAM 상주 서빙 중인 모델과 다를 경우, 백엔드 `llama_manager.load_model_with_download(requested_model)`를 자동 호출하여 원자적 핫스왑을 수행한다.

**Independent Test**: `uv run pytest tests/unit/test_dynamic_model_switch.py`로 다른 모델 요청 시 핫스왑 동작 및 동일 모델 요청 시 핫스왑 생략 검증

### Tests for User Story 1 ⚠️

- [x] T003 [P] [US1] Create unit test for dynamic model hot-swap routing in `tests/unit/test_dynamic_model_switch.py`

### Implementation for User Story 1

- [x] T004 [US1] Implement dynamic model ID extraction and `llama_manager.load_model_with_download` invocation in `src/api/routes/inference_api.py`
- [x] T005 [US1] Enforce `asyncio.Lock` serialization and error handling for hot-swap operations in `src/core/llama_manager.py`

**Checkpoint**: User Story 1 complete - `POST /v1/chat/completions` automatically hot-swaps models dynamically.

---

## Phase 4: User Story 2 - sample_04_model_switch.py & openai_04_model_switch.py 실측 검증 (Priority: P1) 🎯 MVP

**Goal**: 예제 실습 스크립트 실행 시 카탈로그 가용 모델 순회에 따라 실제 VRAM 모델 전환 및 고유 생성 결과/TPS 실측이 정상 처리되도록 보장한다.

**Independent Test**: `uv run sample/sample_04_model_switch.py` 및 `uv run sample/openai_04_model_switch.py` 실행 시 100% 정상 완진

### Tests for User Story 2 ⚠️

- [x] T006 [P] [US2] Create unit test for sample model switch execution in `tests/unit/test_sample_model_switch.py`

### Implementation for User Story 2

- [x] T007 [P] [US2] Refine httpx model switch sample script in `sample/sample_04_model_switch.py`
- [x] T008 [P] [US2] Refine OpenAI SDK model switch sample script in `sample/openai_04_model_switch.py`

**Checkpoint**: User Story 2 complete - both sample scripts perform live model hot-swapping and print performance metrics cleanly.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Full regression suite validation and quickstart scenario checks

- [x] T009 Run full unit test suite via `uv run pytest tests/unit/ --ignore=tests/unit/test_legacy_extraction_llm.py --ignore=tests/unit/test_e2e_serving.py --ignore=tests/unit/test_embedding_reranker_serving.py`
- [x] T010 Execute end-to-end validation scenarios documented in `specs/116-fix-model-switching/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) completion
- **User Story 2 (Phase 4)**: Depends on User Story 1 (Phase 3) completion
- **Polish (Phase 5)**: Depends on Phase 3 and Phase 4 completion

### User Story Dependencies

- **US1 (P1)**: Foundational -> US1 implementation
- **US2 (P1)**: Depends on US1 (uses the dynamic hot-swap functionality of US1)

---

## Implementation Strategy

### MVP Scope

1. Complete Phase 1 (Setup) & Phase 2 (Foundational)
2. Complete Phase 3 (User Story 1 - Dynamic Model Hot-Swap in `inference_api.py`)
3. Validate User Story 1 independently with `tests/unit/test_dynamic_model_switch.py`
4. Complete Phase 4 (User Story 2 - Sample Scripts)
5. Run full regression tests (Phase 5)
