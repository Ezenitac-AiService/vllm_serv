# Tasks: 서버 현황 모니터링 불일치 해소 및 헬스체크 통일

**Input**: Design documents from `/specs/085-unify-monitoring-healthchecks/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are MANDATORY per Constitution Principle II & VII.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- Single project structure: `scripts/`, `src/core/`, `tests/integration/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify monitoring script files and paths

- [X] T001 Verify script permissions and parameters in `scripts/status_server.sh` and `scripts/diagnose_server_health.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Multi-IP resolution logic in shell script that MUST be complete before health check testing

- [X] T002 Add LAN IP (`10.0.0.41`) and multi-loopback IP discovery logic to `scripts/status_server.sh`

---

## Phase 3: User Story 1 - 모니터링 진단 도구 간 헬스체크 결과 100% 일치 (Priority: P1) 🎯 MVP

**Goal**: Ensure `./status_server.sh` and `diagnose_server_health.py` output 100% consistent `Port 8082 OPEN` and `HTTP 200 OK` status when the dashboard is running.

**Independent Test**: Execute `./status_server.sh` and `uv run scripts/diagnose_server_health.py` and verify identical 8082 OPEN status.

### Tests for User Story 1 (MANDATORY)

- [X] T003 [P] [US1] Create integration test for healthcheck status consistency in `tests/integration/test_server_health_diagnostics_consistency.py`

### Implementation for User Story 1

- [X] T004 [US1] Update `scripts/status_server.sh` dashboard HTTP probe to test `127.0.0.1`, `localhost`, and LAN IP using `curl -sL --max-time 5`
- [X] T005 [US1] Align DOM keyword verification regex and fallback socket check in `scripts/status_server.sh` with `scripts/diagnose_server_health.py`

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and regression testing

- [X] T006 [P] Execute quickstart validation scenarios in `specs/085-unify-monitoring-healthchecks/quickstart.md`
- [X] T007 Run regression test suite on diagnostics (`uv run pytest tests/integration/test_server_health_diagnostics_consistency.py -v`)


---

## Dependencies & Execution Order

- **Phase 1 (Setup)** -> **Phase 2 (Foundational)** -> **Phase 3 (User Story 1)** -> **Phase 4 (Polish)**
