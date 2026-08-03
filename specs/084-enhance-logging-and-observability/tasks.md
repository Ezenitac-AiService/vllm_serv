# Tasks: 서버 진단 로그 강화 및 포트 점유(Errno 98) 정밀 추적 고도화

**Input**: Design documents from `/specs/084-enhance-logging-and-observability/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are MANDATORY per Constitution Principle II & VII - implementation without tests is prohibited.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- Single project structure: `src/core/`, `src/api/`, `scripts/`, `tests/unit/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify server configurations and logging infrastructure

- [X] T001 Verify server configuration parameters and log directory paths in `config/server_config.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core process and port cleanup automation that MUST be complete before user story testing

**⚠️ CRITICAL**: No user story implementation can proceed until zombie processes and port binding conflicts are resolved.

- [X] T002 Update `scripts/stop_server.sh` to kill `llama_cpp.server` python module processes and clean up sockets on ports 8081, 8082, 8089, 8090, 8091
- [X] T003 Implement `_cleanup_zombie_on_port(port)` socket release helper in `src/core/process_manager.py` before spawning subprocesses

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - 실측 로그 기반 정밀 에러 트레이싱 (Priority: P1) 🎯 MVP

**Goal**: Record Python tracebacks, exception details, and subprocess exit codes in `logs/error.log` and `logs/server.log` to cure opaque 503 errors.

**Independent Test**: Execute `uv run scripts/diagnose_server_health.py` and verify detailed error messages and clean 200 OK responses.

### Tests for User Story 1 (MANDATORY) ⚠️

> **NOTE: Write these tests FIRST, ensure they fail or catch opaque errors before implementation**

- [X] T004 [P] [US1] Create unit test for multi-line traceback logging in `tests/unit/test_error_traceback_logging.py`
- [X] T005 [P] [US1] Create unit test for port cleanup in `tests/unit/test_process_manager_port_cleanup.py`

### Implementation for User Story 1

- [X] T006 [US1] Enhance `ClientAccessLogMiddleware` in `src/api/middleware/client_access_logger.py` to record multi-line `traceback.format_exc()` on 5xx/4xx responses into `logs/error.log`
- [X] T007 [US1] Update reverse proxy error handlers in `src/api/routes/inference_api.py` to log exception details and target port on 503 responses
- [X] T008 [US1] Enhance `ProcessManager._drain_stdout()` in `src/core/process_manager.py` to capture stderr context on non-zero exit code and write to `logs/error.log`
- [X] T009 [US1] Update `scripts/diagnose_server_health.py` to print exact 503 failure details on endpoint check failure

**Checkpoint**: User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - 포트 8089/8090/8091 강제 정돈 및 바인딩 보장 (Priority: P1)

**Goal**: Ensure clean process startup without `[Errno 98] address already in use` conflicts.

**Independent Test**: Run `./stop_server.sh` and verify all ports are 100% released and `AuxiliaryManager` stays healthy.

### Implementation for User Story 2

- [X] T010 [US2] Update `AuxiliaryManager` in `src/core/auxiliary_manager.py` to enforce circuit breaker limits and log `DISABLED` state transitions cleanly
- [X] T011 [US2] Execute `./stop_server.sh` followed by `./start_server.sh` and verify all ports (8081, 8082, 8089, 8090, 8091) start cleanly without Errno 98 errors

**Checkpoint**: User Story 1 and User Story 2 work independently and harmoniously.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Full regression testing and validation against project constitution

- [X] T012 [P] Execute quickstart validation guide scenarios in `specs/084-enhance-logging-and-observability/quickstart.md`
- [X] T013 Run full test suite regression (`uv run pytest tests/ -v`) per Constitution Principle VII



---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS User Story 1 & 2
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion - Primary MVP deliverable
- **User Story 2 (Phase 4)**: Depends on Foundational phase completion - Port cleanup and circuit breaker
- **Polish (Phase 5)**: Depends on User Story 1 and User Story 2 completion

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2)
- **User Story 2 (P1)**: Can start after Foundational (Phase 2)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (T002, T003)
3. Complete Phase 3: User Story 1 (T004 ~ T009)
4. Complete Phase 4: User Story 2 (T010, T011)
5. Run full test suite regression (Phase 5)
