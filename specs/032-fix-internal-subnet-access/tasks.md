# Tasks: 서비스 플랫폼 사설망(192.168.0.x) 듀얼 랜 포트(Dual NIC) 호스트 IP 기반 동적 서브넷 허용 및 접근 차단 해제 (032-fix-internal-subnet-access)

**Input**: Design documents from `/specs/032-fix-internal-subnet-access/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and network profile configuration verification

- [x] T001 Verify platform profiles and network configuration setup in `config/platform_profiles.json` and `src/core/network_detector.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Base network detector multi-NIC inspection verification

- [x] T002 [P] Verify `NetworkDetector.get_active_lan_ips()` multi-NIC detection logic in `src/core/network_detector.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - 서비스 플랫폼 듀얼 랜 포트에 부여된 모든 실제 LAN IP 기반 192.168.0.x 사설망 클라이언트 동적 접속 허용 (Priority: P1) 🎯 MVP

**Goal**: 듀얼 랜 포트(Dual NIC) 활성 IP를 탐지하여 `192.168.0.0/16` 및 사설망 CIDR 대역을 `SubnetFilterMiddleware`의 `allowed_subnets`에 런타임 합집합으로 동적 주입하고 `config/platform_profiles.json`에도 2중 동기화하여 `192.168.0.x` 사설망 클라이언트 접근 차단(HTTP 403)을 해제

**Independent Test**: `192.168.0.x` 사설 IP를 가진 클라이언트의 API 요청 시 `SubnetFilterMiddleware`에서 HTTP 403 Forbidden 에러 없이 HTTP 200 OK 응답을 반환함을 검증

### Tests for User Story 1 (MANDATORY)

- [x] T003 [P] [US1] Write unit and integration tests for dual NIC active LAN IP detection and 192.168.0.x client access in `tests/integration/test_subnet_security.py` and `tests/unit/test_network_detector.py`

### Implementation for User Story 1

- [x] T004 [US1] Update `config/platform_profiles.json` allowed_subnets for `legacy-i7-930-gtx1070` and `pascal-avx2-gtx1080ti` to explicitly include `"192.168.0.0/16"` and `"10.0.0.0/8"`
- [x] T005 [US1] Update `src/api/server.py` and `src/core/config_manager.py` to dynamically construct `allowed_subnets` by merging `NetworkDetector.get_active_lan_ips()` CIDRs with base subnets
- [x] T006 [US1] Run unit and integration tests `tests/integration/test_subnet_security.py` to verify 192.168.0.x access is allowed and 403 Forbidden is prevented for active LAN IP subnets

**Checkpoint**: User Story 1 (MVP) complete and testable independently

---

## Phase 4: User Story 2 - 듀얼 NIC 멀티 포트 감지 및 ConfigManager 런타임 LAN IP 동적 결합 (Priority: P2)

**Goal**: `ConfigManager.get_detected_network_info()`에서 듀얼 랜 포트의 활성 사설 IP 목록과 CIDR 서브넷 대역을 합집합으로 조립하여 반환하도록 고도화

**Independent Test**: `ConfigManager.get_detected_network_info()` 호출 시 듀얼 랜 포트 활성 IP 서브넷이 포함된 결합 `allowed_subnets` 목록이 반환됨을 검증

### Tests for User Story 2 (MANDATORY)

- [x] T007 [P] [US2] Write unit test for `ConfigManager.get_detected_network_info()` allowed_subnets union merging in `tests/unit/test_config_manager_profiles.py`

### Implementation for User Story 2

- [x] T008 [US2] Update `src/core/config_manager.py` `get_detected_network_info()` to return the merged dynamic CIDR list for dual NIC active IPs

**Checkpoint**: User Stories 1 AND 2 functional and verified

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Overall validation, Quickstart guide execution, and regression testing

- [x] T009 [P] Run full `uv run pytest` test suite to verify 0 regressions across all unit/integration tests
- [x] T010 Run quickstart validation guide in `specs/032-fix-internal-subnet-access/quickstart.md` to verify dual NIC subnet access and firewall status

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS User Stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) completion (MVP)
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2) and US1 completion
- **Polish (Phase 5)**: Depends on User Stories 1 and 2 completion

### User Story Dependencies

- **User Story 1 (P1)**: Independent MVP story
- **User Story 2 (P2)**: Builds upon US1 dynamic CIDR detection logic to expose merged network info in ConfigManager

### Parallel Opportunities

- T002 (Foundational network detector check) can run in parallel with T001
- T003 [US1] test can be written in parallel
- T007 [US2] test can be written in parallel
- T009 [Polish] pytest run can be executed in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Complete Phase 1 & Phase 2 (T001, T002)
2. Complete Phase 3 (T003 - T006)
3. Validate User Story 1 independently (`192.168.0.x` 사설망 접근 차단 해제 및 듀얼 NIC 활성 IP 동적 주입 검증)

### Incremental Delivery
1. Deliver US1 (서비스 플랫폼 192.168.0.x 동적 서브넷 허용 및 403 해제)
2. Deliver US2 (듀얼 NIC network_info 동적 CIDR 합집합 결합)
3. Perform Phase 5 Polish & Quickstart Validation
