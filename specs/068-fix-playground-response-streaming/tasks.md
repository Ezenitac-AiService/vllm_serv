# Tasks: AI Playground SSE 스트리밍 응답 렌더링 및 Qwen/DeepSeek 사고 과정 파싱 보장 (068-fix-playground-response-streaming)

**Input**: Design documents from `/specs/068-fix-playground-response-streaming/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project structure and dashboard route environment verification

- [X] T001 Verify project dashboard API environment and file locations in `src/api/routes/dashboard_api.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core contract schema verification before user story implementation

- [X] T002 [P] Verify SSE streaming contract schema in `specs/068-fix-playground-response-streaming/contracts/playground-stream-contract.json`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - AI Playground SSE 스트리밍 응답 렌더링 및 Qwen/DeepSeek 사고 과정 파싱 (Priority: P1) 🎯 MVP

**Goal**: `POST /dashboard/api/playground/stream` 스트리밍 파서에서 `reasoning_content` / `reasoning` / `content` / `text` 키 파싱 및 live `<think>` 과정 실시간 UI 전송 보장.

**Independent Test**: AI Playground UI 또는 `POST /dashboard/api/playground/stream` 엔드포인트 호출 시 SSE 데이터 청크(`think`, `text`, `metrics`)가 정상 전달되고 대답이 시각화되는지 100% 확인.

### Implementation for User Story 1

- [X] T003 [P] [US1] Add reasoning_content and reasoning chunk parsing to run_playground_stream in `src/api/routes/dashboard_api.py`
- [X] T004 [P] [US1] Add check_llama_status preflight check to run_playground_stream in `src/api/routes/dashboard_api.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - MetricsDB 자동 복구 및 신규 구축 검증 테스트 (Priority: P2)

**Goal**: DB 파일 삭제 후 시스템 재구축 시에도 `MetricsDB` 지연 로딩 싱글톤과 시드 주입이 오류 없이 작동하는지 검증.

**Independent Test**: `uv run pytest tests/unit/test_metrics_db.py tests/unit/test_dashboard_api.py` 실행 시 100% Green Pass 통과.

### Implementation for User Story 2

- [X] T005 [P] [US2] Add unit tests for reasoning_content streaming chunks and llama status check in `tests/unit/test_dashboard_api.py`
- [X] T006 [P] [US2] Add unit test for MetricsDB fresh database reconstruction and seeding in `tests/unit/test_metrics_db.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently and pass tests

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final end-to-end verification and full suite regression testing

- [X] T007 [P] Run quickstart validation scenarios in `specs/068-fix-playground-response-streaming/quickstart.md`
- [X] T008 Execute full regression test suite (`uv run pytest`) per DoD-004

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
- T003, T004 in User Story 1 can be developed in parallel in `src/api/routes/dashboard_api.py`
- T005, T006 in User Story 2 can be developed in parallel in `tests/unit/test_dashboard_api.py` and `tests/unit/test_metrics_db.py`
- T007 in Polish phase can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & 2 (Setup & Foundational)
2. Complete Phase 3 (User Story 1)
3. **STOP and VALIDATE**: Verify AI Playground streaming independently

### Incremental Delivery

1. Complete Setup + Foundational
2. Implement US1 (`src/api/routes/dashboard_api.py`) -> Validate MVP
3. Implement US2 (`tests/unit/test_dashboard_api.py`, `tests/unit/test_metrics_db.py`) -> Validate unit test suite
4. Run full regression test suite (`uv run pytest`) for DoD-004
