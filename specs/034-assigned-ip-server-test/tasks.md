---

description: "Task list for Assigned IP Server Verification Test implementation"
---

# Tasks: Assigned IP Server Verification Test (할당된 IP 기반 서버 구동 검증 테스트)

**Input**: Design documents from `/specs/034-assigned-ip-server-test/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included for each user story and must be executed using `uv run pytest`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- File paths are explicitly included in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for the verifier component

- [x] T001 Create `src/core/server_connectivity_verifier.py` module file with initial imports and class shell
- [x] T002 [P] Create unit test file `tests/unit/test_server_connectivity_verifier.py` with test fixtures shell

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data structures that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 [P] Implement `IPTestVerdict`, `ConnectivityReport`, and `ServerNetworkContext` dataclasses in `src/core/server_connectivity_verifier.py`
- [x] T004 Integrate `src/core/server_connectivity_verifier.py` with existing `NetworkDetector` from `src/core/network_detector.py`

**Checkpoint**: Foundation ready - data structures and detector imports in place.

---

## Phase 3: User Story 1 - Loopback 및 할당 IP 접속 검증 (Priority: P1) 🎯 MVP

**Goal**: Verify HTTP GET connection, API call, and HTTP 200 OK response for `127.0.0.1` and all assigned non-loopback LAN IPs (including dual LAN ports).

**Independent Test**: `uv run pytest tests/integration/test_server_assigned_ip.py -v`

### Tests for User Story 1

- [x] T005 [P] [US1] Write unit tests for single IP HTTP verification in `tests/unit/test_server_connectivity_verifier.py`
- [x] T006 [P] [US1] Write integration test skeleton for server connectivity in `tests/integration/test_server_assigned_ip.py`

### Implementation for User Story 1

- [x] T007 [US1] Implement `ServerConnectivityVerifier.verify_ip()` to send HTTP GET requests and record status, HTTP response code, and response time in `src/core/server_connectivity_verifier.py`
- [x] T008 [US1] Implement `ServerConnectivityVerifier.verify_all()` to iterate over target IPs and return `ConnectivityReport` in `src/core/server_connectivity_verifier.py`
- [x] T009 [US1] Complete integration test assertions in `tests/integration/test_server_assigned_ip.py` verifying loopback and assigned LAN IPs response

**Checkpoint**: At this point, User Story 1 is fully functional and testable independently (MVP ready).

---

## Phase 4: User Story 2 - 동적 IP 탐지 및 테스트 바인딩 (Priority: P2)

**Goal**: Dynamically discover all active non-loopback IPv4 addresses (including dual LAN ports) using `NetworkDetector` and construct test target URLs.

**Independent Test**: `uv run pytest tests/unit/test_server_connectivity_verifier.py -k test_get_target_ips`

### Tests for User Story 2

- [x] T010 [P] [US2] Write unit test for `ServerConnectivityVerifier.get_target_ips()` in `tests/unit/test_server_connectivity_verifier.py`

### Implementation for User Story 2

- [x] T011 [US2] Implement `ServerConnectivityVerifier.get_target_ips()` combining `127.0.0.1` and `NetworkDetector.get_active_lan_ips()` in `src/core/server_connectivity_verifier.py`

**Checkpoint**: User Story 2 adds dynamic multi-NIC/dual-LAN IP discovery to the verifier.

---

## Phase 5: User Story 3 - 네트워크 예외 및 바인딩 실패 진단 (Priority: P3)

**Goal**: Provide clear, detailed diagnostic messages (connection refused, timeout, specific failed IP info) when an assigned IP fails to connect or respond.

**Independent Test**: `uv run pytest tests/unit/test_server_connectivity_verifier.py -k test_exception_handling`

### Tests for User Story 3

- [x] T012 [P] [US3] Write unit tests simulating ConnectionRefused and Timeout errors in `tests/unit/test_server_connectivity_verifier.py`

### Implementation for User Story 3

- [x] T013 [US3] Implement exception handling (`urllib.error.URLError`, `socket.timeout`) and detailed error diagnostics in `src/core/server_connectivity_verifier.py`
- [x] T014 [US3] Update `tests/integration/test_server_assigned_ip.py` to assert diagnostic log output when an assigned IP is unreachable

**Checkpoint**: All user stories (P1, P2, P3) complete with full error reporting.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and end-to-end suite validation

- [x] T015 [P] Update validation scenarios in `specs/034-assigned-ip-server-test/quickstart.md`
- [x] T016 Run full test suite using `uv run pytest` to ensure zero regressions across existing codebase
