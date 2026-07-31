# Tasks: SQLite MetricsDB 손상 시 자동 격리 및 자가 복구 파이프라인 (066-metrics-db-auto-recovery)

**Input**: Design documents from `/specs/066-metrics-db-auto-recovery/`

**Prerequisites**: [plan.md](file:///home/dev/storage/vllm_serv/specs/066-metrics-db-auto-recovery/plan.md), [spec.md](file:///home/dev/storage/vllm_serv/specs/066-metrics-db-auto-recovery/spec.md), [research.md](file:///home/dev/storage/vllm_serv/specs/066-metrics-db-auto-recovery/research.md), [data-model.md](file:///home/dev/storage/vllm_serv/specs/066-metrics-db-auto-recovery/data-model.md), [quickstart.md](file:///home/dev/storage/vllm_serv/specs/066-metrics-db-auto-recovery/quickstart.md)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and MetricsDB exception handling inspection

- [x] T001 Inspect existing `src/core/metrics_db.py` initialization and connection exception handling

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement quarantine helper for corrupt database files in `src/core/metrics_db.py`

- [x] T002 Implement `quarantine_corrupt_db()` helper in `src/core/metrics_db.py` to backup `.db`, `.db-wal`, `.db-shm` files to `data/metrics.db.corrupt_<timestamp>`

**Checkpoint**: Foundation ready - user story implementation can begin

---

## Phase 3: User Story 1 - SQLite 데이터베이스 손상 감지 시 자동 격리 및 복구 (`src/core/metrics_db.py`) (Priority: P1) 🎯 MVP

**Goal**: Catch `sqlite3.DatabaseError` / `OperationalError` during `_get_connection()` / `_init_db()` and execute quarantine + auto-recreation (with `:memory:` fallback).

**Independent Test**: Initialize `MetricsDB()` with a malformed `data/metrics.db` file and verify server startup completes without crash.

### Implementation for User Story 1

- [x] T003 [US1] Wrap `_get_connection()` and `_init_db()` in `src/core/metrics_db.py` with `DatabaseError` / `OperationalError` exception handlers that trigger `quarantine_corrupt_db()` and re-initialize schema
- [x] T004 [US1] Implement In-Memory DB (`:memory:`) fallback mechanism in `src/core/metrics_db.py` when filesystem write/rename operations fail

**Checkpoint**: User Story 1 fully functional — corrupt metrics DB automatically quarantined and recreated without crashing server.

---

## Phase 4: User Story 2 - MetricsDB 손상 자가 복구 단위 테스트 (`tests/unit/test_metrics_db.py`) (Priority: P2)

**Goal**: Build comprehensive unit test suite injecting corrupted SQLite files and verifying quarantine backups and recovery.

**Independent Test**: Run `uv run pytest tests/unit/test_metrics_db.py` and verify 100% Green Pass.

### Tests for User Story 2 ⚠️

- [x] T005 [P] [US2] Add unit tests in `tests/unit/test_metrics_db.py` for malformed DB file quarantine, WAL file cleanup, and post-recovery `log_request()` / `get_summary()` operations

**Checkpoint**: User Story 2 fully functional — unit test suite asserting database corrupt recovery.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Quickstart validation and full regression test suite execution

- [x] T006 Run quickstart validation scenarios documented in `quickstart.md`
- [x] T007 Run full regression test suite (`uv run pytest`) to ensure 100% Green Pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1) → User Story 2 (P2)
- **Polish (Phase 5)**: Depends on all user stories being complete

### Parallel Opportunities

- T005 can run in parallel with polish/docs tasks after US1 implementation

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup (Phase 1) and Foundational (Phase 2)
2. Complete User Story 1 (Phase 3)
3. Validate recovery by instantiating `MetricsDB` with corrupt file

### Incremental Delivery

1. Deliver MVP (`metrics_db.py` quarantine & auto-recreation)
2. Create unit tests in `tests/unit/test_metrics_db.py`
3. Execute full regression suite (`uv run pytest`)
