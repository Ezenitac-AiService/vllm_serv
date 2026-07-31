# Tasks: Inference API Reverse Proxy Content-Length Header Handling Fix (069-fix-proxy-content-length-header)

**Input**: Design documents from `/specs/069-fix-proxy-content-length-header/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify inference API route file location and setup

- [X] T001 Verify inference API route file location in `src/api/routes/inference_api.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Verify core contract schema before implementation

- [X] T002 [P] Verify proxy header filter contract schema in `specs/069-fix-proxy-content-length-header/contracts/proxy-header-filter-contract.json`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Reverse Proxy 응답 헤더 필터링 및 정상 통신 보장 (Priority: P1) 🎯 MVP

**Goal**: `reverse_proxy` 반환 시 `content-length`, `transfer-encoding`, `content-encoding`, `connection` 제어 헤더 제외 필터링 적용.

**Independent Test**: `sample_01_chat.py` 실행 및 `POST /v1/chat/completions` 호출 시 100% 정상 수신 검증.

### Implementation for User Story 1

- [X] T003 [P] [US1] Exclude content-length, transfer-encoding, content-encoding, and connection headers in reverse_proxy in `src/api/routes/inference_api.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - 헤더 필터링 단위 테스트 및 회귀 검증 (Priority: P2)

**Goal**: `reverse_proxy` 응답 헤더 필터링 및 스트리밍 기능 단위 테스트 작성.

**Independent Test**: `uv run pytest tests/unit/test_inference_api_proxy_headers.py` 실행 시 100% Green Pass 통과.

### Implementation for User Story 2

- [X] T004 [P] [US2] Add unit test for proxy response header filtering in `tests/unit/test_inference_api_proxy_headers.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently and pass tests

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final end-to-end verification and full suite regression testing

- [X] T005 [P] Run quickstart validation scenarios in `specs/069-fix-proxy-content-length-header/quickstart.md`
- [X] T006 Execute full regression test suite (`uv run pytest`) per DoD-003

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on User Story 1 component implementation
- **Polish (Phase 5)**: Depends on all user story tasks completion

### Parallel Opportunities

- T002 in Foundational can run in parallel
- T003 in User Story 1 can be developed in `src/api/routes/inference_api.py`
- T004 in User Story 2 can be developed in `tests/unit/test_inference_api_proxy_headers.py`
- T005 in Polish phase can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & 2 (Setup & Foundational)
2. Complete Phase 3 (User Story 1)
3. **STOP and VALIDATE**: Verify reverse proxy request independently

### Incremental Delivery

1. Complete Setup + Foundational
2. Implement US1 (`src/api/routes/inference_api.py`) -> Validate MVP
3. Implement US2 (`tests/unit/test_inference_api_proxy_headers.py`) -> Validate unit test suite
4. Run full regression test suite (`uv run pytest`) for DoD-003
