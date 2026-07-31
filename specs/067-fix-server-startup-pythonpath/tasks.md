# Tasks: start_server.sh 데몬 구동시 PYTHONPATH 예외 및 0.0.0.0 curl 바인딩 오류 수정 (067-fix-server-startup-pythonpath)

**Input**: Design documents from `/specs/067-fix-server-startup-pythonpath/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure verification

- [X] T001 Verify project control script environment and file locations in `scripts/start_server.sh` and `scripts/status_server.sh`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure and contract verification before user story implementation

- [X] T002 [P] Verify control script contract schema in `specs/067-fix-server-startup-pythonpath/contracts/server-control-contract.json`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - `start_server.sh` 구동 시 `PYTHONPATH` 보장 및 `uv run` 데몬 안정 구동 (Priority: P1) 🎯 MVP

**Goal**: `./start_server.sh` 구동 시 `ModuleNotFoundError`로 인한 백그라운드 프로세스 사멸 방지, `0.0.0.0` 호스트 `127.0.0.1` curl 헬스체크 변환, `MetricsDB` 탑레벨 로딩 디스크 크래시 차단, 및 Fail-Fast 진단로그 출력 보장.

**Independent Test**: `./start_server.sh` 실행 후 `./status_server.sh` 조회 시 `프로세스 상태: 🟢 구동 중 (RUNNING)` 및 PID 유지가 100% 정상 작동하는지 확인.

### Implementation for User Story 1

- [X] T003 [P] [US1] Convert MetricsDB instantiation to Lazy Singleton Proxy pattern in `src/core/metrics_db.py`
- [X] T004 [P] [US1] Update daemon launch command to `uv run` and add Fail-Fast diagnostic logging in `scripts/start_server.sh`
- [X] T005 [P] [US1] Implement 0.0.0.0 to 127.0.0.1 CURL_HOST fallback logic in `scripts/status_server.sh`
- [X] T006 [US1] Verify seed pack packaging of updated control scripts in `scripts/make_seed_pack.sh`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - 서버 제어 스크립트 결합 검증 테스트 (`tests/unit/test_seed_pack_legacy.py`) (Priority: P2)

**Goal**: 단위 테스트 수트를 통해 `start_server.sh`, `status_server.sh` 구동 로직, curl 호스트 변환, `MetricsDB` 지연 로딩을 자동 검증.

**Independent Test**: `uv run pytest tests/unit/test_seed_pack_legacy.py` 실행 시 100% Green Pass 통과.

### Implementation for User Story 2

- [X] T007 [P] [US2] Add unit tests for uv run daemon launch command and 0.0.0.0 host conversion in `tests/unit/test_seed_pack_legacy.py`
- [X] T008 [P] [US2] Add unit test for MetricsDB Lazy Singleton Proxy initialization in `tests/unit/test_seed_pack_legacy.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently and pass tests

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final end-to-end verification and full suite regression testing

- [X] T009 [P] Run quickstart validation scenarios in `specs/067-fix-server-startup-pythonpath/quickstart.md`
- [X] T010 Execute full regression test suite (`uv run pytest`) per DoD-005

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
- T003, T004, T005 in User Story 1 can be developed in parallel across `src/core/metrics_db.py`, `scripts/start_server.sh`, and `scripts/status_server.sh`
- T007, T008 in User Story 2 can be developed in parallel in `tests/unit/test_seed_pack_legacy.py`
- T009 in Polish phase can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch core component and script updates in parallel:
Task: "Convert MetricsDB instantiation to Lazy Singleton Proxy pattern in src/core/metrics_db.py"
Task: "Update daemon launch command to uv run and add Fail-Fast diagnostic logging in scripts/start_server.sh"
Task: "Implement 0.0.0.0 to 127.0.0.1 CURL_HOST fallback logic in scripts/status_server.sh"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & 2 (Setup & Foundational)
2. Complete Phase 3 (User Story 1)
3. **STOP and VALIDATE**: Verify `./start_server.sh` and `./status_server.sh` independently

### Incremental Delivery

1. Complete Setup + Foundational
2. Implement US1 (`src/core/metrics_db.py`, `scripts/start_server.sh`, `scripts/status_server.sh`) -> Validate MVP
3. Implement US2 (`tests/unit/test_seed_pack_legacy.py`) -> Validate unit test suite
4. Run full regression test suite (`uv run pytest`) for DoD-005
