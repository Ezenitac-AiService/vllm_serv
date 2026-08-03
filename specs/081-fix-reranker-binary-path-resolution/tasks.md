# Tasks: `llama-server` 네이티브 바이너리 경로 바인딩 및 `/v1/rerank` 404 근본 해결 (`081-fix-reranker-binary-path-resolution`)

**Input**: Design documents from `/specs/081-fix-reranker-binary-path-resolution/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project environment and initial verification setup

- [x] T001 Verify project environment and uv virtual environment configuration

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infrastructure and base definitions for binary path resolution

- [x] T002 Inspect existing binary detection logic in src/core/process_manager.py

**Checkpoint**: Foundation ready - user story implementation can begin

---

## Phase 3: User Story 1 - llama-server 네이티브 바이너리 경로 탐지 확장 (Priority: P1) 🎯 MVP

**Goal**: ProcessManager.verify_and_build_llama_server()의 탐지 대상 경로에 /usr/local/lib/ollama/llama-server 및 추가 표준 시스템 경로를 추가하여 네이티브 바이너리로 Reranker 백엔드를 바인딩하고 /v1/rerank 404 에러를 해결합니다.

**Independent Test**: verify_and_build_llama_server() 실행 결과 build_source가 PYTHON_MODULE_FALLBACK이 아닌 네이티브 경로로 감지되는지 단정하고, sample_04_reranking.py 실행 시 HTTP 200 OK 응답을 확인합니다.

### Tests for User Story 1 (MANDATORY) ⚠️

- [x] T003 [P] [US1] Create unit tests for native binary detection in tests/unit/test_process_manager_binary_path.py
- [x] T004 [P] [US1] Create contract test for reranker response contract in tests/unit/test_reranker_contract.py

### Implementation for User Story 1

- [x] T005 [US1] Extend candidate binary search paths in src/core/process_manager.py verify_and_build_llama_server() to include /usr/local/lib/ollama/llama-server and /opt/ollama/lib/ollama/llama-server
- [x] T006 [US1] Ensure Reranker process spawn logic in src/core/process_manager.py utilizes the resolved native llama-server binary with --reranking --embedding options

**Checkpoint**: At this point, User Story 1 is fully functional and testable independently

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Validation, regression testing, and verification against Constitution VII

- [x] T007 [P] Execute quickstart validation script sample_04_reranking.py to verify /v1/rerank returns 200 OK
- [x] T008 Run full regression test suite via uv run pytest tests/ -v per Constitution Principle VII

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS User Story 1
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **Polish (Phase 4)**: Depends on User Story 1 completion

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - Primary MVP deliverable

### Within User Story 1

- Tests MUST be written and fail first (T003, T004)
- Path resolution logic implementation (T005) before process spawn verification (T006)

### Parallel Opportunities

- T003 and T004 can run in parallel (different test files)
- T007 can run independently during polish phase

---

## Parallel Example: User Story 1

```bash
# Launch test creation tasks in parallel:
Task: "Create unit tests for native binary detection in tests/unit/test_process_manager_binary_path.py"
Task: "Create contract test for reranker response contract in tests/unit/test_reranker_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Verify binary resolution with pytest and sample_04_reranking.py
5. Run full test suite regression (Phase 4)
