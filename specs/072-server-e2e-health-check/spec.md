# Feature Specification: LLM 서버 서비스 모델, API 엔드포인트, E2E 대시보드, 방화벽 및 LAN 접속 통합 진단 스펙 (072-server-e2e-health-check)

**Feature Branch**: `072-server-e2e-health-check`

**Created**: 2026-08-03

**Status**: Draft

**Input**: User description: "LLM 서버가 어떤 모델들을 서비스하고 있는지, API 엔드포인트들이 다 잘 작동하는지, 웹 대시보드 E2E 테스트, 방화벽 상태 확인, 서버의 IP 기반으로 내부 네트워크의 다른 IP에서 접속이 잘 되는지 전부 테스트하는 스펙 작성"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - LLM 서빙 모델 및 전체 API 엔드포인트 헬스체크 (Priority: P1) 🎯 MVP

서버 관리자 및 사용자는 LLM 서빙 데몬이 가동될 때 서빙 중인 LLM 모델 목록(`/v1/models`)을 확인하고, 주요 API 엔드포인트(`/v1/chat/completions`, `/v1/completions`, `/health`)의 헬스체크 및 추론 응답이 정상 작동하는지 자동 진단할 수 있어야 합니다.

**Why this priority**: LLM 서빙의 기본 기능(모델 제공 및 추론 API) 작동 여부를 보장하는 최우선 필수 기능입니다.

**Independent Test**: 진단 CLI 도구 또는 테스트 스크립트 실행 시 현재 가동 중인 모델 이름(예: `qwen3.5-4b`) 및 API 200 OK 응답 상태를 동적으로 수집하고 보고할 수 있는지 확인.

**Acceptance Scenarios**:

1. **Given** LLM 서버가 구동 중인 상태일 때, **When** 모델 목록 API(`/v1/models`)를 호출하면, **Then** 현재 서빙 중인 서빙 모델 명칭 리스트와 함께 HTTP 200 OK 상태코드를 반환해야 합니다.
2. **Given** 주요 API 엔드포인트 점검 수행 시, **When** `/v1/chat/completions` 및 `/health` 엔드포인트에 헬스체크 요청을 전송하면, **Then** 3초 이내에 정상 추론 응답 및 헬스 상태가 반환되어야 합니다.

---

### User Story 2 - 서버 실 IP 감지 및 내부 네트워크(LAN) 바인딩/방화벽 접속 검증 (Priority: P1) 🎯 MVP

네트워크 관리자 및 운영자는 테스트 구동 플랫폼(`10.0.0.x`)과 실제 서비스 배포 플랫폼(`192.168.0.x`) 등 다양한 LAN 환경에서 서버의 실제 IP 주소를 자동 감지하고, 방화벽(Firewall/Port) 바인딩 상태 및 동종 네트워크 타 IP에서의 접속 가능 여부를 사전 검증할 수 있어야 합니다.

**Why this priority**: 개발 플랫폼 IP와 서비스 플랫폼 IP가 분리되어 있으므로, 127.0.0.1이 아닌 실제 바인딩 IP를 기반으로 내부 네트워크망 통신이 가능해야 합니다.

**Independent Test**: 실제 LAN IP 감지 모듈(`NetworkDetector`)을 통해 감지된 IP와 8081/8082 포트에 대해 방화벽 허용 및 소켓 접속 테스트를 수행하여 정상 바인딩 상태를 검증.

**Acceptance Scenarios**:

1. **Given** 네트워크 환경 진단 시, **When** 진단 모듈을 구동하면, **Then** 서버의 실제 바인딩 IP(예: `10.0.0.x` 또는 `192.168.0.x`)를 감지하고 `127.0.0.1` / `localhost`가 아닌 실제 IP 주소로 방화벽 포트(8081, 8082 등) 접속 가능 여부를 체크해야 합니다.
2. **Given** 방화벽(Firewall) 상태 점검 시, **When** 포트 바인딩 및 방화벽 차단 여부를 테스트할 때, **Then** 지정 포트가 외부/내부망에 차단되지 않고 외부 수신(LISTEN) 가능 상태인지 여부를 판별하여 리포트해야 합니다.

---

### User Story 3 - 웹 대시보드 E2E 브라우저 UI 자동 검증 (Priority: P2)

운영자는 웹 브라우저 기반 대시보드 UI(8082 포트 등)가 브라우저 단에서 정상 렌더링되고, 주요 대시보드 요소 및 텍스트가 렌더링 오류 없이 유저에게 표시되는지 E2E 자동 테스트로 검증받기를 원합니다.

**Why this priority**: CLI API 테스트뿐만 아니라 사용자가 접하는 웹 대시보드 UI의 실제 브라우저 렌더링 상태까지 자동 검증하여 E2E 신뢰성을 확보합니다.

**Independent Test**: Playwright 브라우저 E2E 테스트 스크립트를 통해 웹 대시보드 URL 접속 후 핵심 UI 렌더링 요소를 자동 확인.

**Acceptance Scenarios**:

1. **Given** 대시보드 웹 서버가 구동 중일 때, **When** E2E 브라우저 진단을 실행하면, **Then** 대시보드 메인 페이지가 렌더링되고 404/500 에러 없이 정상 UI 화면이 수집되어야 합니다.

### Edge Cases

- 서버 IP가 다중 NIC(복수 랜카드)로 구성된 경우 활성화된 LAN 서브넷 IP를 정확히 감지 및 바인딩 점검
- 서버가 미구동 상태이거나 포트가 닫혀있는 경우 무한 대기 없이 명확한 타임아웃 오류 메시지 반환
- 웹 대시보드 접속 시 브라우저 헤드리스(Headless) 환경에서도 렌더링 타임아웃 없이 정상 테스트 수행

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: 서빙 중인 LLM 모델 목록 수집 및 주요 API 엔드포인트(`/v1/models`, `/v1/chat/completions`, `/health`) 자동 진단 기능 구현
- **DoD-002**: 동적 LAN IP 감지 기반 방화벽(Port Listen) 및 내부 네트워크 통신 접속 검증 로직 수록
- **DoD-003**: 웹 대시보드 UI 접속 및 브라우저 E2E 검증 테스트 수트 구축
- **DoD-004**: 전체 종합 헬스체크 진단 스크립트 실행 시 통합 리포트 출력 및 pytest 수트 Pass 통과

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 시스템은 현재 서빙 중인 LLM 모델의 명칭 목록을 `/v1/models` API 조회를 통해 동적으로 수집하고 검증해야 합니다.
- **FR-002**: 시스템은 LLM 서빙 API 엔드포인트(`chat/completions`, `completions`, `health`)에 대해 실제 응답 가능 상태를 자동 테스트해야 합니다.
- **FR-003**: 시스템은 `127.0.0.1`에 의존하지 않고 서버의 실제 유효 LAN IP(`10.0.0.x` 또는 `192.168.0.x`)를 감지하여 포트 바인딩 및 네트워크 수신 가능 여부를 검증해야 합니다.
- **FR-004**: 시스템은 서버의 방화벽(Firewall) 상태 및 지정 포트(8081, 8082 등)의 개방 상태를 자동 점검해야 합니다.
- **FR-005**: 시스템은 웹 대시보드 인터페이스에 대한 브라우저 기반 E2E UI 렌더링 검증 테스트를 수행해야 합니다.

### Key Entities

- **ServerHealthReport**: 모델 목록, API 엔드포인트 응답 상태, LAN IP 감지 결과, 방화벽 개방 상태, 웹 대시보드 E2E 상태를 수집하는 종합 진단 결과 개체

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 헬스체크 구동 시 모델 목록 및 3종 주요 API 엔드포인트 상태 진단 성공률 100%
- **SC-002**: 실제 LAN IP 감지 및 포트 바인딩/방화벽 통과 여부 검증 성공률 100%
- **SC-003**: 웹 대시보드 E2E 브라우저 테스트 렌더링 및 헬스체크 통과율 100%

## Assumptions

- LLM 메인 서버는 기본 8081 포트에서 OpenAI 호환 API를 제공하고, 대시보드 웹 서버는 기본 8082 포트에서 서비스를 제공합니다.
- 테스트 환경에는 E2E 브라우저 테스트를 위한 Playwright 또는 브라우저 진단 패키지가 준비되어 있습니다.
