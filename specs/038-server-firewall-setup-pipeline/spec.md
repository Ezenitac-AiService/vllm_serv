# Feature Specification: 서버 방화벽 구축 파이프라인 전수 검토 및 포트 개방 자동화 (038-server-firewall-setup-pipeline)

**Feature Branch**: `038-server-firewall-setup-pipeline`  
**Created**: 2026-07-30  
**Status**: Draft  
**Input**: User description: "지금 대화 기록 볼수 있지? 답답해 미칠거 같은데 대시보드 접속이 안된다니까, 방화벽 열으라는데, 우리 setup.sh가 서버 셋팅할때 방화벽 설정 안함? 우리 서버 구축 파이프라인 전부 검토해"

---

## Clarifications

### Session 2026-07-30

- Q: 방화벽 개방 및 예외 처리 정책 → A: TTY 터미널 감지 시 `sudo ufw allow 8081/tcp 8089/tcp` 대화형 비밀번호 입력을 호출하고, 비대화형 환경 시 명확한 경고와 해결 명령 출력 (Option A)
- Q: 실물 네트워크 및 방화벽 검증 테스트 작성 규격 → A: 목업/더미 패스 금지. 실제 OS 물리 소켓 바인딩/연결 및 커널 방화벽 룰셋(`ufw`/`iptables`) 실측 조회를 통한 100% 실체화 검증 (Option A)

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 서버 구축 및 구동 시 OS 방화벽 포트 자동 검증 및 개방 (Priority: P1) 🎯 MVP

서버 관리자 또는 개발자가 `./scripts/setup.sh` 또는 `./scripts/start_server.sh`를 실행할 때, 프로젝트 서빙 포트(`8081/tcp`, `8089/tcp`)가 OS 방화벽(`ufw`, `iptables`, `firewalld`)에 정상 등록되었는지 자동으로 진단하고, 필요한 경우 개방 규칙을 확실히 적용합니다.

**Why this priority**: 방화벽 포트 미개방으로 인해 동일 내부망 클라이언트(`10.0.0.x`)에서 웹 대시보드 및 LLM API 접속이 차단되는 문제점을 근본적으로 해결합니다.

**Independent Test**: 방화벽이 활성화된 환경에서 `./scripts/setup.sh` 또는 `./scripts/start_server.sh` 구동 시 `8081/tcp` 및 `8089/tcp` 방화벽 상태를 진단하고 실패 없이 개방 규칙이 적용되는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** ufw 방화벽이 활성화되어 있고 8081 포트가 닫힌 환경에서, **When** `./scripts/setup.sh` 또는 `./scripts/start_server.sh`를 실행하면, **Then** 방화벽 상태를 진단하고 비대화형 `sudo -n` 실패 시 대화형 TTY `sudo ufw allow` 비밀번호 입력을 유도하거나 명확한 해결 가이드를 제공합니다.
2. **Given** 8081/tcp 포트가 이미 방화벽에 등록된 환경에서, **When** 스크립트를 구동하면, **Then** "이미 포트가 개방되어 있음"을 확인하고 대기 시간 없이 즉시 다음 단계로 진행합니다.

---

### User Story 2 - non-interactive sudo 환경 및 비권한 사용자를 위한 방화벽 자동 진단 진단서 및 헬프 가이드 (Priority: P2)

비대화형 CI/CD 진입점이거나 `sudo` 비밀번호 입력이 필요하여 자동으로 포트를 개방하지 못할 경우, 무음 에러로 방치되지 않고 뚜렷한 진단 경고와 즉시 복구 가능한 명시적 터미널 명령어를 출력합니다.

**Why this priority**: 자동 개방 실패 시 사용자가 원인을 몰라 대시보드 미접속 원인을 방화벽으로 인지하지 못하는 상황을 방지합니다.

**Independent Test**: 비밀번호 없는 sudo 권한이 없는 환경에서 스크립트 실행 시 뚜렷한 방화벽 진단 경고와 정확한 실행 명령(`sudo ufw allow 8081/tcp`)이 출력되는지 확인합니다.

**Acceptance Scenarios**:

1. **Given** 비밀번호 입력이 필요한 sudo 환경에서, **When** 포트 개방 시도가 거부되면, **Then** 붉은색/노란색 강조 로그로 원인과 실행할 수동 명령(`sudo ufw allow 8081/tcp`)을 명시적으로 안내합니다.

---

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `scripts/setup.sh`, `scripts/start_server.sh`, `src/core/firewall_manager.py` 파이프라인 전수 검토 및 방화벽 진단/개방 강화
- **DoD-002**: `8081/tcp` (대시보드/API) 및 `8089/tcp` (백엔드) 포트에 대한 방화벽 자동 검증 단위 테스트 작성 및 통과
- **DoD-003**: `sudo -n` 실패 시 대화형 TTY 감지 및 수동 가이드 명령 명확화
- **DoD-004**: 테스트 코드 작성 시 목업/하드코딩 패스 금지 및 실제 OS 소켓/방화벽 실측 통과 보장

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `setup.sh` 및 `start_server.sh` 스크립트는 실행 시 OS 방화벽(`ufw`, `iptables`, `firewalld`) 활성화 여부와 `8081/tcp`, `8089/tcp` 포트 개방 상태를 전수 점검해야 한다.
- **FR-002**: TTY 대화형 터미널 환경인 경우 `sudo ufw allow 8081/tcp` 및 `sudo ufw allow 8089/tcp`를 직접 호출하여 사용자가 비밀번호를 입력해 즉시 포트를 개방하도록 유도해야 한다.
- **FR-003**: 비대화형 환경에서 `sudo` 권한 미획득으로 방화벽 자동 개방 실패 시, 명확한 진단 박스 로그와 함께 즉시 복구 가능한 해결 명령어(`sudo ufw allow 8081/tcp`)를 안내해야 한다.
- **FR-004**: `FirewallManager` 파이썬 모듈(`src/core/firewall_manager.py`)은 ufw, firewalld, iptables 상태를 정확히 감지하고 포트 개방 결과를 불리언 지표로 반환해야 한다.
- **FR-005**: 서버 가동 시 `/dashboard/` 및 `/v1/chat/completions` 접근을 방화벽 미개방으로 차단당하지 않도록 사전 점검(Pre-flight Check)을 수행해야 한다.
- **FR-006**: 검증 테스트 파이프라인은 인메모리 목업(In-memory Mock), 더미 폴백, 하드코딩 패스 단정을 엄격히 금지하며, 실제 OS 물리 소켓 연결 프로브(`socket.create_connection`) 및 활성 커널 방화벽 룰셋 파싱(`ufw status`)을 통해 100% 실체 검증해야 한다.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 방화벽이 닫힌 서버 환경에서 `./scripts/setup.sh` 실행 시 8081/tcp 포트 개방 상태 진단 성공률 100%
- **SC-002**: 포트 미개방으로 인한 403 / Connection Timeout 차단 발생 시 사용자가 10초 이내에 복구 명령어를 파악할 수 있도록 뚜렷한 진단 메시지 표출
- **SC-003**: 이미 포트가 열린 환경에서 추가 포트 개방 시도로 인한 가동 지연 0초
- **SC-004**: 네트워크 및 방화벽 테스트 코드의 목업 의존도 0% 달성 (실물 소켓 및 OS 룰셋 실측)

---

## Assumptions

- 서버 OS는 Linux (Ubuntu/Debian 또는 RHEL/CentOS 계열)이며 `ufw` 또는 `firewalld`가 설치되어 있거나 사용 가능함.
- 동일 내부망 네트워크(`10.0.0.0/8`, `192.168.0.0/16`)의 클라이언트 컴퓨터에서 HTTP 포트(`8081`)로 직접 접근하는 표준 운용 환경을 전제로 함.
