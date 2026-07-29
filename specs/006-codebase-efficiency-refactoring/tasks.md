# Tasks: 코드베이스 구조 개선 및 효율화 리팩토링 (Codebase Efficiency Refactoring)

**Input**: Design documents from `/specs/006-codebase-efficiency-refactoring/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Project root: `/home/dev/storage/vllm_serv/`
- Core modules: `src/core/`
- API routes: `src/api/routes/`
- Tests: `tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Define core data models and type interfaces required across all refactored modules

- [x] T001 Define `ProcessStatusEnum` (`UNLOADED`, `LOADING`, `READY`, `ERROR`) in `src/core/process_manager.py`
- [x] T002 Define immutable `ProcessState` Pydantic v2 model (`frozen=True`) with fields (`status`, `model_id`, `port`, `pid`, `error_message`, `exit_code`) in `src/core/process_manager.py`
- [x] T003 Define `EventPayload` Pydantic schema (`status`, `model_id`, `n_ctx`, `vram_usage_mb`, `error`) in `src/core/event_broadcaster.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Prepare shared test infrastructure and mock setups before component refactoring

- [x] T004 Create unit test fixtures and subprocess mock helpers in `tests/unit/test_llama_manager.py`
- [x] T005 Create atomic file I/O test fixtures with temporary directory mocks in `tests/unit/test_config_manager.py`

---

## Phase 3: User Story 1 - 서브프로세스 관리 및 이벤트 디스패치 구조 분리 (Priority: P1) 🎯 MVP

**Goal**: `LlamaManager` 단일 클래스의 책임을 `ProcessManager` (서브프로세스 라이프사이클)와 `EventBroadcaster` (SSE 이벤트 전파)로 분리하고 Bounded Queue와 15초 하트비트를 적용한다.

**Independent Test**: `ProcessManager`와 `EventBroadcaster` 단위 테스트 통과 및 SSE 스트림 15초 `: ping\n\n` 하트비트 수신 검증.

### Implementation for User Story 1

- [x] T006 [P] [US1] Implement `ProcessManager.spawn_process()` with port selection and subprocess creation in `src/core/process_manager.py`
- [x] T007 [P] [US1] Implement `ProcessManager.stop_process()` with `SIGTERM` timeout, `SIGKILL` escalation, and `await process.wait()` zombie process reaping (FR-009) in `src/core/process_manager.py`
- [x] T008 [P] [US1] Implement `ProcessManager.get_vram_limit()` hardware VRAM lookup dictionary in `src/core/process_manager.py`
- [x] T009 [P] [US1] Implement `EventBroadcaster` listener management, Bounded Queue (`maxsize=100`), and Full Snapshot Event injection on overflow (FR-011) in `src/core/event_broadcaster.py`
- [x] T010 [P] [US1] Implement 15-second heartbeat ping generator (`: ping\n\n`) (FR-007) in `src/core/event_broadcaster.py`
- [x] T011 [US1] Refactor `LlamaManager` in `src/core/llama_manager.py` to compose `ProcessManager` and `EventBroadcaster` as internal delegates
- [x] T012 [US1] Add unit tests for `ProcessManager` state transitions and `EventBroadcaster` queue overflow handling in `tests/unit/test_llama_manager.py`

**Checkpoint**: User Story 1 complete - LlamaManager modularized with ProcessManager and EventBroadcaster.

---

## Phase 4: User Story 2 - 원자적 파일 I/O 및 설정 관리 모듈 안정성 강화 (Priority: P1)

**Goal**: `ConfigManager`의 파일 읽기/쓰기를 동일 디렉토리 원자적 쓰기(`tempfile.NamedTemporaryFile(dir=os.path.dirname(config_path))` + `os.replace`) 및 메모리 캐싱으로 개선하여 `EXDEV` 에러와 동시성 데이터 오염을 차단한다.

**Independent Test**: 동시 쓰기 시 임시 파일 교체 및 `os.replace`로 정합성을 유지하는 단위 테스트 통과.

### Implementation for User Story 2

- [x] T013 [US2] Implement `ConfigManager._write_atomic()` using `tempfile.NamedTemporaryFile(dir=os.path.dirname(config_path))`, explicit `os.chmod(0o600)` (FR-008), and `os.replace` in `src/core/config_manager.py`
- [x] T014 [US2] Implement in-memory configuration caching and `get_config()` cache invalidation logic in `src/core/config_manager.py`
- [x] T015 [US2] Add unit tests for `ConfigManager` atomic write and cache hit/miss behavior in `tests/unit/test_config_manager.py`

**Checkpoint**: User Story 2 complete - ConfigManager atomic file I/O and caching verified.

---

## Phase 5: User Story 3 - 라우터/미들웨어 비동기 프록시 효율화 및 코드 가독성 개선 (Priority: P2)

**Goal**: FastAPI `lifespan` 내에 싱글톤 `httpx.AsyncClient` 커넥션 풀을 바인딩하고, 추론 프록시 시 클라이언트 이탈(`request.is_disconnected()`) 캔슬레이션을 적용한다.

**Independent Test**: 추론 API 스트리밍 중 이탈 감지 캔슬레이션 및 `uv run pytest` 100% 통과.

### Implementation for User Story 3

- [x] T016 [US3] Implement `@asynccontextmanager` `lifespan` handler in `src/api/main.py` to initialize `app.state.http_client` with `httpx.Limits(max_connections=100)` and `aclose()` teardown
- [x] T017 [US3] Refactor `inference_api.py` in `src/api/routes/inference_api.py` to retrieve `request.app.state.http_client` from state
- [x] T018 [US3] Add `request.is_disconnected()` streaming loop cancellation check with `try...finally` `await response.aclose()` cleanup (FR-010) in `src/api/routes/inference_api.py`
- [x] T019 [P] [US3] Refactor `dashboard_api.py` in `src/api/routes/dashboard_api.py` with explicit Pydantic response models and type annotations

**Checkpoint**: User Story 3 complete - Connection pooling and disconnect cancellation implemented.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and full regression test execution

- [x] T020 [P] Execute full 10-test regression suite (`uv run pytest`) and verify 100% test pass rate
- [x] T021 Validate end-to-end quickstart scenarios in `specs/006-codebase-efficiency-refactoring/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Independent of US1, can run after Foundational phase
- **User Story 3 (Phase 5)**: Depends on US1 & US2 completion
- **Polish (Phase 6)**: Depends on all user stories being complete

### Parallel Opportunities

- T006, T007, T008, T009, T010 can run in parallel
- T013, T014 can run in parallel with US1 tasks
- T019 can run in parallel with T017, T018

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & Phase 2
2. Complete Phase 3 (User Story 1: `ProcessManager` & `EventBroadcaster`)
3. **STOP and VALIDATE**: Verify modularized process management and SSE broadcasting

### Incremental Delivery

1. Setup + Foundational -> Infrastructure ready
2. User Story 1 -> ProcessManager & EventBroadcaster modularization
3. User Story 2 -> Atomic replace ConfigManager
4. User Story 3 -> Lifespan AsyncClient & Disconnect cancellation
5. Polish -> 100% pytest regression pass
