# Tasks: Chat Endpoint 503 Fix & Llama Server Binary Resolution Refactoring

**Input**: Design documents from `/specs/082-fix-chat-endpoint-503/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are MANDATORY per Constitution Principle II & VII - implementation without tests is prohibited.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- Single project structure: `src/core/`, `src/api/`, `tests/unit/`, `tests/e2e/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify server configurations and baseline infrastructure

- [X] T001 Verify server configuration parameters in `config/server_config.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core `ProcessManager` binary resolution refinement that MUST be complete before user story testing

**⚠️ CRITICAL**: No user story implementation can proceed until candidate path filtering is established.

- [X] T002 Exclude Ollama internal library paths (`/usr/local/lib/ollama/llama-server`, `/opt/ollama/...`) from `ProcessManager.verify_and_build_llama_server()` candidate scan in `src/core/process_manager.py`
- [X] T003 Implement `subprocess` sanity check (`--help` execution test) for `llama-server` binary candidates in `src/core/process_manager.py`

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - OpenAI 규격 채팅 엔드포인트(/v1/chat/completions) 정상 응답 회복 (Priority: P1) 🎯 MVP

**Goal**: Restore 200 OK responses for `/v1/chat/completions` API requests and cure 503 Service Unavailable errors.

**Independent Test**: Execute `uv run samples/sample_01_chat.py` and verify HTTP 200 OK with valid generated completion text.

### Tests for User Story 1 (MANDATORY) ⚠️

> **NOTE: Write these tests FIRST, ensure they fail or catch invalid Ollama path resolution before implementation**

- [X] T004 [P] [US1] Create unit tests verifying Ollama internal path exclusion in `tests/unit/test_process_manager_binary_path.py`
- [X] T005 [P] [US1] Create contract test for `/v1/chat/completions` response structure in `tests/unit/test_chat_completion_contract.py`

### Implementation for User Story 1

- [X] T006 [US1] Ensure `LlamaManager` backend startup cleanly initializes `llama-server` process on port 8089 in `src/core/llama_manager.py`
- [X] T007 [US1] Update 503 reverse proxy readiness guard in `src/api/routes/inference_api.py` to route `/v1/chat/completions` requests when backend is ready
- [X] T008 [US1] Execute health check script `uv run scripts/diagnose_server_health.py` to verify `/v1/chat/completions` is OPEN (200 OK)
- [X] T009 [US1] Execute E2E sample script `uv run samples/sample_01_chat.py` to verify 200 OK completion

**Checkpoint**: User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - ProcessManager 스탠드얼론 실행 검증 및 보조 인스턴스 격리 (Priority: P2)

**Goal**: Ensure `ProcessManager` rejects non-standalone binaries and `AuxiliaryManager` isolates port 8089 from auxiliary process cleanup.

**Independent Test**: Run `uv run pytest tests/unit/test_process_manager_binary_path.py` and verify binary validation behavior and process isolation.

### Tests for User Story 2 (MANDATORY) ⚠️

- [X] T010 [P] [US2] Create unit test for binary sanity check execution (`--help` test) in `tests/unit/test_process_manager_binary_path.py`

### Implementation for User Story 2

- [X] T011 [US2] Ensure `AuxiliaryManager` port cleanup in `src/core/auxiliary_manager.py` strictly targets specified ports (8090/8091) without affecting port 8089
- [X] T012 [US2] Verify `llama-cpp-python` module fallback works smoothly when no standalone binary exists in `src/core/process_manager.py`

**Checkpoint**: User Story 1 and User Story 2 work independently and harmoniously.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Full regression testing and validation against project constitution

- [X] T013 [P] Execute quickstart validation guide scenarios in `specs/082-fix-chat-endpoint-503/quickstart.md`
- [X] T014 Run full test suite regression (`uv run pytest tests/ -v`) per Constitution Principle VII

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS User Story 1 & 2
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion - Primary MVP deliverable
- **User Story 2 (Phase 4)**: Depends on Foundational phase completion - Can run after or in parallel with US1
- **Polish (Phase 5)**: Depends on User Story 1 and User Story 2 completion

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Focuses on binary sanity and process isolation

### Within Each User Story

- Tests MUST be written and fail first (T004, T005, T010)
- Foundational binary filtering (T002, T003) before process startup (T006)
- Core implementation before endpoint routing update (T007)
- Validation scripts (T008, T009) at the end of User Story 1

### Parallel Opportunities

- T004 and T005 can run in parallel (different test files)
- T010 and T013 can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch test creation tasks in parallel:
Task: "Create unit tests verifying Ollama internal path exclusion in tests/unit/test_process_manager_binary_path.py"
Task: "Create contract test for /v1/chat/completions response structure in tests/unit/test_chat_completion_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Verify `/v1/chat/completions` with `samples/sample_01_chat.py`
5. Run full test suite regression (Phase 5)
