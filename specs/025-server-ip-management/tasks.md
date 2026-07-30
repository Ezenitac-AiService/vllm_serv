# Tasks: 듀얼 랜포트 다중 NIC 환경 서버 IP 바인딩 및 네트워크 관리 로직 고도화 (025-server-ip-management)

**Input**: Design documents from `/specs/025-server-ip-management/`

**Prerequisites**: [plan.md](file:///home/dev/storage/vllm_serv/specs/025-server-ip-management/plan.md), [spec.md](file:///home/dev/storage/vllm_serv/specs/025-server-ip-management/spec.md), [research.md](file:///home/dev/storage/vllm_serv/specs/025-server-ip-management/research.md), [data-model.md](file:///home/dev/storage/vllm_serv/specs/025-server-ip-management/data-model.md), [quickstart.md](file:///home/dev/storage/vllm_serv/specs/025-server-ip-management/quickstart.md)

**Tests**: 테스트 코드는 헌장 II원칙(테스트 주도 개발 및 품질 보증)에 따라 모든 기능 변경 시 검증과 함께 작성 및 실행됩니다.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [TaskID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (`[US1]`, `[US2]`, `[US3]`)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project configuration layout & schema verification

- [x] T001 Verify project structure and specification files at `specs/025-server-ip-management/`
- [x] T002 Update `config/server_config.json` schema to include default `host: "0.0.0.0"` and `firewall_auto_allow: true`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models and foundational unit test scaffolding that MUST be complete before user story scripts can execute

**⚠️ CRITICAL**: All user story tasks depend on the data models and base test structures in this phase.

- [x] T003 [P] Create `NetworkInterfaceInfo` and `ServerNetworkConfig` dataclasses in `src/core/network_detector.py`
- [x] T004 [P] Create unit test scaffold for active network interface scanner in `tests/unit/test_network_detector.py`
- [x] T005 [P] Create unit test scaffold for OS firewall (ufw/iptables) management in `tests/unit/test_firewall_manager.py`

**Checkpoint**: Foundation ready - network data structures and test harnesses ready.

---

## Phase 3: User Story 1 - 외부 LAN IP 접속 지원 및 다중 NIC 바인딩 허용 (Priority: P1) 🎯 MVP

**Goal**: Enable host binding to `0.0.0.0`, propagate to `llama-server` sub-processes, allow external LAN IP (`192.168.0.80`) requests without CORS/subnet errors, and handle OS firewall port opening.

**Independent Test**: `curl -i http://192.168.0.80:8081/health` and `curl -i http://192.168.0.80:8081/v1/models` return HTTP 200 OK from external host.

### Tests for User Story 1 ⚠️

- [x] T006 [P] [US1] Add integration test for multi-NIC external IP access and SubnetFilter in `tests/integration/test_subnet_security.py`
- [x] T007 [P] [US1] Update `tests/unit/test_config_manager.py` to test `0.0.0.0` host binding and active IP extraction

### Implementation for User Story 1

- [x] T008 [P] [US1] Implement `NetworkDetector` class in `src/core/network_detector.py` to scan active NICs, filter loopback & unassigned ports, and extract valid IPv4 LAN addresses
- [x] T009 [P] [US1] Implement `FirewallManager` class in `src/core/firewall_manager.py` to attempt `ufw allow` / `iptables` commands for ports `8081`, `8089` and log non-root permission warnings gracefully
- [x] T010 [US1] Update `src/core/config_manager.py` to integrate `NetworkDetector`, `FirewallManager`, and default `0.0.0.0` host binding
- [x] T011 [US1] Update `src/core/process_manager.py` to propagate `--host 0.0.0.0` to `llama-server` sub-processes
- [x] T012 [US1] Update `src/core/subnet_filter.py` and `src/api/server.py` to dynamically authorize detected LAN IPs (`192.168.0.0/16`) and configure FastAPI CORS `allow_origins`

**Checkpoint**: At this point, User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - 듀얼 랜포트 미할당 이더넷 예외 처리 및 활성 IP 자동 탐지 (Priority: P2)

**Goal**: Handle dual-NIC servers with one unassigned/down Ethernet port without socket binding errors or exception crashes.

**Independent Test**: Server starts cleanly when 2nd LAN port is disconnected/unassigned and binds to active LAN IP (`192.168.0.80`).

### Tests for User Story 2 ⚠️

- [x] T013 [P] [US2] Add unit test in `tests/unit/test_network_detector.py` for dual LAN port with unassigned interface (down/no IPv4)

### Implementation for User Story 2

- [x] T014 [US2] Update `src/core/network_detector.py` with defensive exception handling and logging for missing/down network interfaces during startup and health check

**Checkpoint**: User Stories 1 AND 2 work independently and smoothly.

---

## Phase 5: User Story 3 - 타겟 플랫폼 프로필별 네트워크 구성 및 학습/서빙 플랫폼 연동 (Priority: P3)

**Goal**: Integrate network binding rules and allowed subnets into `config/platform_profiles.json` for 3 machine platforms (`e3-1231v3`, `i7-4770`, `i7-930`).

**Independent Test**: Selecting each platform profile accurately loads network binding parameters.

### Tests for User Story 3 ⚠️

- [x] T015 [P] [US3] Add unit tests for platform profile network loading in `tests/unit/test_config_manager_profiles.py`

### Implementation for User Story 3

- [x] T016 [US3] Update `config/platform_profiles.json` with network configuration blocks for `e3-1231v3`, `i7-4770`, and `i7-930`
- [x] T017 [US3] Update `src/core/config_manager.py` to parse and apply network settings from platform profiles

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification, codebase audit, and test execution

- [x] T018 [P] Perform codebase audit to verify no hardcoded `127.0.0.1` host restrictions remain in server setup
- [x] T019 Run complete pytest test suite (`uv run pytest tests/`) to ensure 100% test pass rate
- [x] T020 Execute quickstart validation scenarios documented in `specs/025-server-ip-management/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1) → User Story 2 (P2) → User Story 3 (P3)
- **Polish (Final Phase)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Enhances `NetworkDetector` exception handling
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Integrates platform profile network configs

### Parallel Opportunities

- All Foundational tasks marked `[P]` (T003, T004, T005) can run in parallel
- Unit and contract tests T006, T007 can run in parallel
- Implementation tasks marked `[P]` (T008, T009) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch parallel implementation:
Task: T008 "Implement NetworkDetector class in src/core/network_detector.py"
Task: T009 "Implement FirewallManager class in src/core/firewall_manager.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Verify `uv run pytest tests/` and test `curl -i http://192.168.0.80:8081/health`
5. Proceed to User Story 2, 3, and Polish
