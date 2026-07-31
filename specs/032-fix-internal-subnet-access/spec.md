# Feature Specification: 서비스 플랫폼 사설망(192.168.0.x) 듀얼 랜 포트(Dual NIC) 호스트 IP 기반 동적 서브넷 허용 및 접근 차단 해제 (032-fix-internal-subnet-access)

**Feature Branch**: `032-fix-internal-subnet-access`

**Created**: 2026-07-30

**Status**: Draft

**Input**: User feedback: 서비스 플랫폼(`legacy-i7-930-gtx1070` 및 운영 장비)의 듀얼 랜 포트(Dual NIC) 환경에서 실제 부여받은 호스트 LAN IP(`192.168.0.x` 및 `10.x.x.x` 등)를 멀티 스캔하여 클라이언트 사설망 접근 차단을 동적으로 해제하도록 보정.

## Clarifications

### Session 2026-07-30

- Q: 서비스 플랫폼(`legacy-i7-930-gtx1070` 및 커스텀 프로필) 192.168.0.x 접속 허용 범위 설정 → A: 실제 부여받은 호스트 LAN IP(`NetworkDetector.get_active_lan_ips()`)를 자동 탐지하여 해당 IP가 속한 사설 CIDR 대역(`192.168.x.x/24` 또는 `/16`) 및 기본 사설망 대역(`127.0.0.1`, `192.168.0.0/16`, `10.0.0.0/8`, `172.16.0.0/12`)을 런타임에 동적으로 `allowed_subnets`에 자동 병합 및 인가함.
- Q: 서비스 플랫폼 듀얼 랜 포트(Dual NIC) 환경에서의 멀티 사설망 IP 감지 및 서브넷 결합 방식 → A: Option A (`NetworkDetector.scan_interfaces()`가 듀얼 랜 포트(NIC 1, NIC 2)의 모든 활성 LAN IP를 멀티 스캔하여, Down/미할당 포트는 자동 제외하고 각 IP가 속한 서브넷 대역(`192.168.0.0/16`, `10.0.0.0/8`, `172.16.0.0/12`)을 합집합(Union)으로 주입하고 `0.0.0.0` 바인딩 유지)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 서비스 플랫폼 듀얼 랜 포트에 부여된 모든 실제 LAN IP 기반 192.168.0.x 사설망 클라이언트 동적 접속 허용 (Priority: P1) 🎯 MVP

서비스 플랫폼(`legacy-i7-930-gtx1070` 및 모든 서비스 프로필) 장비가 시동될 때, 듀얼 랜 포트(NIC 1, NIC 2)에 실제 할당된 모든 호스트 LAN IP(`192.168.0.x`, `10.x.x.x` 등)를 `NetworkDetector.get_active_lan_ips()`를 통해 멀티 감지하고, 다운되거나 미할당된 포트는 제외한 뒤 활성화된 모든 랜 포트의 서브넷 대역(`192.168.0.0/16`, `10.0.0.0/8`, `172.16.0.0/12`)을 합집합(Union)하여 `SubnetFilterMiddleware`의 허용 서브넷(`allowed_subnets`) 목록에 동적으로 주입함으로써 192.168.0.x 사설망 클라이언트의 접속 거부를 완전 해제합니다.

**Why this priority**: 듀얼 랜 포트 서비스 서버에서 NIC 1(`192.168.0.x`)과 NIC 2 중 일부만 인가되거나 누락될 경우 사설망 클라이언트 접속이 HTTP 403으로 거부되는 현상을 근본적으로 해결하기 위함입니다.

**Independent Test**: 듀얼 랜 포트 활성화 환경에서 NIC 1(`192.168.0.x`) 및 NIC 2 IP로 접속하는 클라이언트 요청에 대해 `SubnetFilterMiddleware` 및 `IpSubnetGuard`가 403 차단 없이 HTTP 200 OK 응답을 반환함을 검증합니다.

**Acceptance Scenarios**:

1. **Given** 서비스 플랫폼(`legacy-i7-930-gtx1070`) 장비의 듀얼 랜 포트에 각각 사설 IP `192.168.0.15` 및 `10.0.1.20`이 할당되어 있을 때, **When** 서버 어플리케이션이 구동되면, **Then** `NetworkDetector.get_active_lan_ips()`를 통해 `192.168.0.0/16` 및 `10.0.0.0/8` 두 서브넷 대역이 모두 `allowed_subnets`에 동적으로 추출 및 포함되어야 한다.
2. **Given** `192.168.0.x` 사설망 클라이언트가 API 및 대시보드 요청을 보낼 때, **When** `SubnetFilterMiddleware`가 요청 IP를 검증하면, **Then** HTTP 403 에러 없이 HTTP 200 OK 성공 응답을 반환해야 한다.

---

### User Story 2 - 듀얼 NIC 멀티 포트 감지 및 ConfigManager 런타임 LAN IP 동적 결합 (Priority: P2)

개발자 및 엔지니어가 `ConfigManager.get_detected_network_info()` 및 서버 구동 설정을 조회할 때, 듀얼 랜 포트의 활성 사설 IP 주소 목록과 서브넷 대역이 `allowed_subnets`에 합집합으로 자동 결합되어 반환됨을 확인합니다.

**Why this priority**: 멀티 NIC 서버 환경에서 단일 포트만 감지되어 접속 불능이 발생하는 현상을 방지하기 위함입니다.

**Independent Test**: `ConfigManager` 및 `SubnetFilterMiddleware` 연동 시 듀얼 랜 포트에서 감지된 모든 LAN IP 대역이 `allowed_subnets`에 자동 포함되어 동작하는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** `ConfigManager.get_server_config()` 또는 `create_app()` 구동 시, **When** 허용 서브넷 목록을 조립하면, **Then** 듀얼 랜 포트에서 감지된 모든 활성 LAN IP 기반 CIDR 대역이 `allowed_subnets` 목록에 자동으로 합집합 병합되어야 한다.

---

### Edge Cases

- 듀얼 랜 포트 중 한 포트가 케이블 미연결(Down) 또는 미할당(APIPA `169.254.x.x`) 상태일 때, 해당 다운 포트는 자동 스킵되고 정상 작동 중인 LAN 포트(`192.168.0.x`)의 서브넷만 정확히 허용되는가?
- 오프라인/루프백(`127.0.0.1`) 전용 환경에서도 예외 없이 기본 로컬 접근이 정상 허용되는가?

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `src/api/server.py` 및 `src/core/config_manager.py`에서 `NetworkDetector.get_active_lan_ips()`를 활용하여 듀얼 랜 포트의 모든 활성 LAN IP 기반 서브넷 대역(`192.168.0.0/16`, `10.0.0.0/8` 등)을 `allowed_subnets`에 동적 합집합 포함하도록 수정 완료
- **DoD-002**: `config/platform_profiles.json` 내 `legacy-i7-930-gtx1070` 및 `pascal-avx2-gtx1080ti` 프로필의 `allowed_subnets`에 `"192.168.0.0/16"` 및 `"10.0.0.0/8"` 추가 동기화 완료
- **DoD-003**: `tests/unit/test_network_detector.py` 및 `tests/integration/test_subnet_security.py` 테스트 수트 업데이트 및 전체 pytest 100% 통과

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (듀얼 랜 포트 활성 LAN IP 기반 동적 서브넷 허용 정책 적용)**: `src/api/server.py` 및 `src/core/config_manager.py` 구동 시 `NetworkDetector.get_active_lan_ips()`로 듀얼 랜 포트의 모든 활성 사설 IP(예: `192.168.0.x`, `10.x.x.x`)를 멀티 스캔하여, Down/미할당 포트를 제외한 전체 사설 CIDR 대역(`192.168.0.0/16`, `10.0.0.0/8`, `172.16.0.0/12`)을 `allowed_subnets` 목록에 동적으로 자동 합성하여 런타임 접근 차단을 완전 해제해야 한다.
- **FR-002 (서비스 플랫폼 듀얼 NIC 서브넷 수록 보장)**: `config/platform_profiles.json` 내 `legacy-i7-930-gtx1070` 및 `pascal-avx2-gtx1080ti`를 비롯한 전체 프로필의 `allowed_subnets`에 `"192.168.0.0/16"` 및 `"10.0.0.0/8"`을 명시적으로 수록하여 사설망 접속 거부를 2중 방지해야 한다.
- **FR-003 (듀얼 랜 포트 서브넷 허용 검증 테스트 수록)**: `tests/unit/test_network_detector.py` 및 `tests/integration/test_subnet_security.py`에 듀얼 랜 포트 LAN IP 탐지 기반 서브넷 인가 검증 테스트를 추가해야 한다.

### Key Entities

- **DynamicSubnetGuard**: `NetworkDetector`에서 듀얼 랜 포트의 활성 IPv4 주소들을 멀티 추출하고 `/24` 및 `/16` CIDR 대역으로 변환하여 `allowed_subnets`에 합집합(Union) 결합하는 런타임 서브넷 인가 엔티티.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 듀얼 랜 포트 서비스 플랫폼에 할당된 실제 IP 대역(`192.168.0.x`) 클라이언트 요청 시 HTTP 403 Forbidden 0건 및 200 OK 통과
- **SC-002**: 전체 pytest 수트 100% 통과

## Assumptions

- `NetworkDetector.get_active_lan_ips()`는 호스트 OS의 모든 활성 LAN IPv4 주소를 정확히 스캔함.
- 사설망 IP 대역 `192.168.0.0/16`은 RFC 1918에 정의된 사설 IP 주소 공간임.
