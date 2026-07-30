# Tasks: 서버 방화벽 구축 파이프라인 전수 검토 및 E2E 실측 테스트 (038-server-firewall-setup-pipeline)

**Input**: Design documents from `/specs/038-server-firewall-setup-pipeline/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `constitution.md` (v1.3.1)  
**Tests**: Real OS Firewall & Physical Host IP (`10.0.0.41:8081`) Playwright E2E tests in `tests/e2e/test_dashboard_e2e.py`

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story mapping ([US1], [US2])

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: E2E test directory creation and Playwright dependencies verification

- [x] T001 Verify `playwright` dependencies in `pyproject.toml` and create `tests/e2e/` directory
- [x] T002 Configure `REAL_NETWORK_TEST` environment flag parser in `tests/conftest.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core OS firewall detection & real socket probe implementation (Anti-Mock Rule)

- [x] T003 Implement non-mocked OS firewall status detector in `src/core/firewall_manager.py`
- [x] T004 Implement real TCP socket connectivity probe helper in `src/core/firewall_manager.py`

**Checkpoint**: Foundational firewall detection utilities ready - User stories can proceed.

---

## Phase 3: User Story 1 - 서버 구축 및 구동 시 OS 방화벽 포트 자동 검증 및 개방 (Priority: P1) 🎯 MVP

**Goal**: TTY 터미널 감지 시 `sudo ufw allow 8081/tcp 8089/tcp` 비밀번호 입력 유도 및 `setup.sh` / `start_server.sh` 자동 개방

**Independent Test**: 방화벽 닫힌 환경에서 `./scripts/setup.sh` 또는 `./scripts/start_server.sh` 구동 시 TTY 승격을 통해 포트가 100% 개방되는지 검증

### Tests for User Story 1

- [x] T005 [P] [US1] Real-execution test for `FirewallManager.allow_port` with real OS process invocation in `tests/unit/test_firewall_manager_real.py`

### Implementation for User Story 1

- [x] T006 [US1] Update `scripts/setup.sh` with TTY detection (`[ -t 1 ]`) and interactive `sudo ufw allow` elevation
- [x] T007 [US1] Update `scripts/start_server.sh` with pre-flight firewall check for ports 8081 and 8089
- [x] T008 [US1] Enhance `FirewallManager.ensure_service_ports_open` in `src/core/firewall_manager.py`

**Checkpoint**: User Story 1 MVP fully functional and testable on physical server.

---

## Phase 4: User Story 2 - non-interactive sudo 환경 및 비권한 사용자를 위한 방화벽 가이드 (Priority: P2)

**Goal**: 비대화형 `sudo -n` 실패 시 붉은색/노란색 강조 로그와 수동 복구 명령어(`sudo ufw allow 8081/tcp`) 안내

**Independent Test**: 비대화형 sudo 실패 환경에서 스크립트 구동 시 즉시 복구 가능한 수동 가이드 블록이 출력되는지 확인

### Tests for User Story 2

- [x] T009 [P] [US2] Integration test for non-interactive sudo warning box formatting in `tests/unit/test_firewall_manager_real.py`

### Implementation for User Story 2

- [x] T010 [US2] Add formatted warning diagnostic banner to `scripts/setup.sh` when `sudo -n` fails
- [x] T011 [US2] Add formatted warning diagnostic banner to `scripts/start_server.sh` when `sudo -n` fails

**Checkpoint**: User Story 2 diagnostic banners operational.

---

## Phase 5: Playwright & Physical IP Network E2E UI Test (Priority: P1)

**Goal**: 서버 실물 IP (`http://10.0.0.41:8081/dashboard/`) 타겟 Playwright E2E 대시보드 UI/UX 사용성 및 소켓 연결 테스트

**Independent Test**: `REAL_NETWORK_TEST=1 uv run pytest tests/e2e/test_dashboard_e2e.py` 실행 시 10.0.0.41 실물 IP로 접속하여 4대 탭 및 프롬프트 테스트 완료 검증

### Tests for Playwright E2E UI

- [x] T012 [P] Playwright E2E test for physical host IP navigation (`http://10.0.0.41:8081/dashboard/`) in `tests/e2e/test_dashboard_e2e.py`
- [x] T013 [P] Playwright E2E test for 4-tab SPA navigation (Monitoring, Control, Playground, Audit) in `tests/e2e/test_dashboard_e2e.py`
- [x] T014 Playwright E2E test for AI Playground prompt submission and response rendering in `tests/e2e/test_dashboard_e2e.py`

**Checkpoint**: Full Playwright E2E UI test suite operational on host LAN IP.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Execution of real test suite and quickstart scenarios

- [x] T015 Run full test suite `uv run pytest tests/unit/ -v`
- [x] T016 Run Playwright E2E test suite `REAL_NETWORK_TEST=1 uv run pytest tests/e2e/test_dashboard_e2e.py -v`
- [x] T017 Execute quickstart scenarios in `specs/038-server-firewall-setup-pipeline/quickstart.md`
