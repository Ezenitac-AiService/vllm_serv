# Feature Specification: 듀얼 랜포트 다중 NIC 환경 서버 IP 바인딩 및 네트워크 관리 로직 고도화 (025-server-ip-management)

**Feature Branch**: `025-server-ip-management`

**Created**: 2026-07-30

**Status**: Draft

**Input**: User description: "e3 1231v3 gtx1080ti는 개발 플렛폼 / i7 4770 rtx 3060는 훈련생 팀프로젝트 플렛폼 - 그래서 llm 서버의 대상은 되지만, 평소에는 모델 학습용으로 gpu 사용중 / i7 930 gtx 1070는 훈련생에게 llm 모델을 제공할 목적의 서비스 플렛폼 / 현재 i7 930에 qwen3.5 모델들은 잘 서비스 되고 있고, 벤치 마크 보고서 생성됨 / 다만 문제가, 192.168.0.80으로 할당된 ip로 들어가면 응답하지 않음 / 서버 보드로 듀얼 랜포트라서 하나의 이더넷은 ip 할당을 받고 있지 않음. / 서버의 ip 관리 로직을 고도화 해야 할것 같음"

## Clarifications

### Session 2026-07-30

- Q: 서버 구동/셋팅 시 OS 방화벽(ufw/iptables) 포트 허용 로직 처리 정책 → A: Option A (서버 셋팅 및 구동 시 ufw/iptables 포트 자동 개방 시도, sudo 권한 필요 시 안내 가이드 및 예외 처리 포함)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 외부 LAN IP 접속 지원 및 다중 NIC 바인딩 허용 (Priority: P1) 🎯 MVP

훈련생 및 외부 개발자가 서비스 플랫폼 서버(i7 930 / GTX 1070)에 할당된 외부 LAN IP(예: `http://192.168.0.80:8081`)로 HTTP 요청을 보낼 때, 기존 `127.0.0.1` 루프백 한계를 넘어 서버가 활성 네트워크 인터페이스(`0.0.0.0` 또는 지정된 LAN IP)에서 요청을 올바르게 바인딩하고 응답해야 합니다.

**Why this priority**: 현재 루프백 전용 바인딩으로 인해 훈련생 서비스 플랫폼(i7 930)에 할당된 외부 IP (`192.168.0.80`)로의 접근이 차단되는 치명적 연결 문제를 해결하는 최우선 과제입니다.

**Independent Test**: `http://192.168.0.80:8081/v1/models` 또는 `/health` 엔드포인트로 외부 네트워크 호스트에서 HTTP GET 요청 전송 시 HTTP 200 OK 응답 수신 가능합니다.

**Acceptance Scenarios**:

1. **Given** 서버가 `0.0.0.0` 호스트 바인딩 모드로 구동 중일 때, **When** 원격 클라이언트가 외부 LAN IP(`http://192.168.0.80:8081/v1/models`)로 접속을 시도하면, **Then** 타임아웃이나 거부 없이 정상적으로 JSON 응답을 반환해야 한다.
2. **Given** `config/server_config.json`에 `host`가 `0.0.0.0`으로 설정된 상태일 때, **When** API 서버 및 `llama-server` 하위 프로세스가 스폰되면, **Then** 두 프로세스 모두 외부 LAN 접속을 수용하는 바인딩 주소를 사용해야 한다.
3. **Given** OS 방화벽이 활성화된 리눅스 서버일 때, **When** 서버 셋팅 또는 구동 절차가 수행되면, **Then** 서비스 포트(`8081`, `8089`)의 방화벽 개방을 자동으로 시도하고 권한 부족 시 가이드 메시지를 로그에 출력해야 한다.

---

### User Story 2 - 듀얼 랜포트 미할당 이더넷 예외 처리 및 활성 IP 자동 탐지 (Priority: P2)

서버 메인보드에 듀얼 랜포트가 존재하는 환경에서, 하나의 이더넷 포트에 IP가 할당되어 있지 않거나 비활성화(Down) 상태이더라도 서버 바인딩 로직이 예외를 발생시키거나 바인딩에 실패하지 않고, 할당된 유효 활성 IP 인터페이스만을 자동 탐지하여 서비스를 정상 개설해야 합니다.

**Why this priority**: 듀얼 NIC 지원 서버 보드(i7 930 메인보드 등)의 미할당 랜포트로 인한 네트워크 탐지 예외 및 잘못된 바인딩 시도를 차단하여 서버 구동 안정성을 보장합니다.

**Independent Test**: 하나의 이더넷 포트에 IP가 연결되지 않은 상태에서 서버 구동 시, 활성 포트 IP(`192.168.0.80`)만 정상 추출되어 바인딩 로그에 출력되고 서비스가 구동되는지 검증 가능합니다.

**Acceptance Scenarios**:

1. **Given** 서버에 듀얼 랜포트 중 1개 포트에만 IP가 할당되어 있을 때, **When** 네트워크 IP 관리 인터페이스 탐지가 수행되면, **Then** 미할당 포트를 안전하게 무시하고 활성 IP(`192.168.0.80`)만을 바인딩 후보 목록에 수집해야 한다.
2. **Given** 활성 네트워크 인터페이스 목록이 변경되거나 미할당 포트가 존재할 때, **When** 서버 헬스체크 및 서브넷 필터링이 작동하면, **Then** 에러 방출 없이 정상 네트워크 소켓 연결을 수용해야 한다.

---

### User Story 3 - 타겟 플랫폼 프로필별 네트워크 구성 및 학습/서빙 플랫폼 연동 (Priority: P3)

프로젝트 내 3종 머신 프로필(개발 플랫폼 `E3 1231v3`, 학습/프로젝트 플랫폼 `i7 4770`, 서비스 플랫폼 `i7 930`)의 역할 차이를 반영하여, 각 플랫폼의 네트워크 바인딩 설정 및 서브넷 허용 목록(`allowed_subnets`)이 `platform_profiles.json`과 연동되어 안전하게 관리되어야 합니다.

**Why this priority**: 평소 모델 학습용으로 사용되지만 LLM 서빙 대상이 되는 `i7 4770` 및 개발 플랫폼 `E3 1231v3`와 서비스 전용 `i7 930` 플랫폼 간의 네트워크 수용 정책을 체계적으로 분리합니다.

**Independent Test**: 각 플랫폼 프로필 선택 시 알맞은 네트워크 바인딩 규칙 및 서브넷 허용 범위가 적용되는지 확인 가능합니다.

---

### Edge Cases

- 듀얼 랜포트 모두 IP가 할당되지 않은 오프라인 환경 구동 시 `127.0.0.1` 루프백 자동 안전 전환
- `allowed_subnets`에 원격 클라이언트 서브넷(`192.168.0.0/24` 등)이 포함되어 있지 않아 HTTP 403 Forbidden 거부되는 현상
- `llama-server` 하위 프로세스가 외부 IP 바인딩 시 포트 충돌(Port Collision) 또는 권한 오류 발생 시 에러 핸들링
- sudo 권한이 없는 환경에서 `ufw` 포트 개방 명령 실패 시 프로세스가 다운되지 않고 권한 안내 메시지를 출력하며 계속 실행

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `src/core/config_manager.py` 및 `config/server_config.json` 내 `host` 바인딩 설정을 `0.0.0.0` 기본 허용 및 외부 접속 지원으로 고도화
- **DoD-002**: 듀얼 NIC 미할당 이더넷 인터페이스 예외 처리 및 활성 IP 자동 탐지 유틸리티 모듈 구현 및 적용
- **DoD-003**: `ProcessManager`의 `llama-server` 스폰 시 `--host 0.0.0.0` (또는 활성 IP) 연동으로 외부 LAN 접속 수용 보장
- **DoD-004**: OS 방화벽(`ufw`/`iptables`) 포트 개방 자동화 및 권한 부족 예외 처리 가이드 모듈 구동 검증
- **DoD-005**: 단위 및 통합 테스트 수트(`pytest tests/`) 100% 통과

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (외부 LAN IP 접속 허용을 위한 호스트 바인딩 고도화)**: `ConfigManager` 및 `server_config.json`의 기본 바인딩 호스트를 외부 접속이 가능한 `0.0.0.0` (또는 활성 LAN IP)으로 설정 가능하게 하고, `ProcessManager`에서 `llama-server` 스폰 시 바인딩 호스트를 외부 접속 가능하게 전파해야 한다.
- **FR-002 (다중 NIC 미할당 인터페이스 자동 탐지 및 예외 처리)**: 듀얼 랜포트 등 다중 네트워크 인터페이스(NIC) 환경에서 IP가 할당되지 않은 포트(Unassigned/Down)는 자동 차단/무시하고, 활성화된 유효 IP 주소만 수집하여 서버 헬스체크 및 바인딩 정보로 활용해야 한다.
- **FR-003 (서브넷 접근 제어 및 CORS 허용 범위 동적 적용)**: `SubnetFilter` 및 FastAPI CORS 미들웨어에서 외부 LAN IP(`192.168.0.80`) 및 동일 대역(`192.168.0.0/24`) 요청이 403 Forbidden이나 CORS 에러 없이 수용되도록 정비해야 한다.
- **FR-004 (플랫폼 프로필 네트워크 명세 일원화)**: `config/platform_profiles.json` 내 3종 머신 플랫폼(`e3-1231v3`, `i7-4770`, `i7-930`) 프로필 명세에 네트워크 바인딩 기본 옵션 및 허용 규칙을 명시하고 연동해야 한다.
- **FR-005 (OS 방화벽 포트 자동 개방 및 셋팅 로직 연동)**: 서버 셋팅 및 구동 시 `ufw` 또는 `iptables` 지원 여부를 자동 탐지하여 서비스 포트(`8081`, `8089` 등)의 방화벽 포트 개방 명령을 시도하고, sudo 권한 부족 시 사용자 안내 가이드 및 경고 로그를 출력해야 한다.

### Key Entities

- **NetworkInterfaceInfo**: 서버 내 개별 NIC의 상태(Interface Name, IP Address, Is Active, Is Loopback).
- **ServerNetworkConfig**: 서버 네트워크 바인딩 규격 (`host`, `port`, `allowed_subnets`, `detected_active_ips`, `firewall_auto_allow`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 할당된 외부 IP(`http://192.168.0.80:8081`) 접속 시 REST API 및 `/health`, `/v1/models` 응답 성공률 **100%**
- **SC-002**: 듀얼 랜포트 미할당 포트 환경에서 서버 개설 시 소켓 바인딩 에러 **0건**
- **SC-003**: 3개 플랫폼 프로필(`e3-1231v3`, `i7-4770`, `i7-930`) 전체에 대한 네트워크 바인딩 정합성 검증

## Assumptions

- 서비스 플랫폼(i7 930 / GTX 1070)은 192.168.0.0/24 내부 공유기 망에 연결되어 있으며 192.168.0.80 IP가 할당되어 있음.
- 듀얼 포트 중 2번째 포트는 물리 케이블 미연결 또는 DHCP 미할당 상태임.
