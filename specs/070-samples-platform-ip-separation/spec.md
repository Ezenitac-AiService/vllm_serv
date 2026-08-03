# Feature Specification: samples 예제 스크립트의 서비스 플랫폼 IP 대역 접속 보장 및 테스트 스크립트 실 IP 검증 분리 명세 (070-samples-platform-ip-separation)

**Feature Branch**: `070-samples-platform-ip-separation`

**Created**: 2026-08-03

**Status**: Draft

**Input**: User description: "테스트 코드들은 서버에서 구동되니까 127.0.0.1이나 localhost가 아닌 실제 IP 기반으로 구동되도록 하고, /home/dev/storage/vllm_serv/samples 의 파일들은 서비스 플랫폼의 IP 대역대인 192.168.0.x에서 서비스 플랫폼으로 접속하는 독립 예제 코드로 작동하도록 분리 명세"

## Clarifications

### Session 2026-08-03

- Q: 개발 플랫폼과 서비스 플랫폼의 IP 대역 구분 및 samples/tests 동작 방식은 무엇인가요? → A: 개발 플랫폼 대역은 `10.0.0.x`, 배포 서비스 플랫폼 대역은 `192.168.0.x`입니다. `tests/`는 실행 환경의 실 IP를 동적 감지하여 `127.0.0.1`/`localhost` 없이 실제 망 접속을 검증하고, `samples/`는 훈련생들이 서비스 플랫폼 주소를 변경/명시하기 쉽도록 `samples/config.json` 또는 `.env` 기반 지정을 지원합니다.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Client Sample 스크립트의 서비스 플랫폼 IP 설정 명시 및 독립성 보장 (Priority: P1) 🎯 MVP

훈련생 및 연동 사용자는 `/home/dev/storage/vllm_serv/samples`에 위치한 Client Sample 스크립트를 사용할 때, 서비스 플랫폼 IP 대역(`192.168.0.x`) 호스트를 `samples/config.json` 또는 `.env` (또는 `SERVER_HOST` 환경변수)를 통해 명시적으로 지정하고 호출할 수 있어야 합니다. 스크립트는 서버 백엔드 모듈에 대한 의존 없이 지정된 호스트 설정을 불러와 동작해야 합니다.

**Why this priority**: 훈련생들이 외부 서비스 플랫폼 접속 환경에서 접속 서버 주소를 손쉽게 변경하고 활용할 수 있는 표준 예제를 제공합니다.

**Independent Test**: `samples/config.json` 또는 `.env` 파일에 지정된 서비스 플랫폼 IP(`192.168.0.x`)를 `samples/common.py`가 올바르게 로드하여 API 호출을 수행하는지 확인.

**Acceptance Scenarios**:

1. **Given** `samples/config.json` 또는 `.env` 파일에 서비스 플랫폼 IP(예: `http://192.168.0.100`)가 지정되어 있을 때, **When** 샘플 스크립트 실행 시, **Then** 지정된 설정 파일의 서버 주소로 요청이 전송되어야 합니다.
2. **Given** 환경변수 `SERVER_HOST`가 전달되는 경우, **When** 샘플 스크립트 실행 시, **Then** 환경변수가 설정 파일 기본값보다 최우선으로 적용되어야 합니다.

---

### User Story 2 - 서버 테스트 스크립트의 동적 실 IP 감지 및 망 접속 검증 (Priority: P2)

QA 및 개발자는 `tests/` 내의 테스트 코드가 실행될 때 현재 개발 플랫폼(`10.0.0.x`) 또는 운영 환경의 실제 네트워크 IP를 동적으로 감지하여 검증을 수행하기를 원합니다. `127.0.0.1` 또는 `localhost` 사용은 금지되며, 동일 네트워크 망 접속 가능 여부를 필수 검증해야 합니다.

**Why this priority**: 테스트 코드는 127.0.0.1 루프백 접속으로 인한 착시를 방지하고, 내부 망 인터페이스에서의 수신 가능 상태를 100% 보장해야 합니다.

**Independent Test**: `tests/conftest.py` 피스처가 실행 플랫폼의 실제 LAN IP(`10.0.0.x` 등)를 감지하여 테스트를 구동하고, `127.0.0.1` 호출이 완전히 차단/제거되었음을 검증.

**Acceptance Scenarios**:

1. **Given** 개발 플랫폼(`10.0.0.x`) 또는 배포 플랫폼 환경일 때, **When** `uv run pytest` 수행 시, **Then** `NetworkDetector` 등을 통해 탐지된 실 IP 기반으로 서버 접속 및 테스트가 이루어져야 합니다.
2. **Given** 테스트 코드 실행 시, **Then** `127.0.0.1` 또는 `localhost`를 접속 대상 호스트로 사용하는 테스트가 없어야 합니다.

### Edge Cases

- `samples/config.json` 파일이 존재하지 않는 경우 기본 예제 설정 파일(`samples/config.json.example`) 제공 및 기본값(`http://192.168.0.100`) 폴백
- `.env` 및 `samples/config.json` 설정 파일 간 우선순위 체계 확립 (`SERVER_HOST` 환경변수 > `.env` / `config.json` > 기본값)

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `samples/` 폴더에 훈련생용 호스트 명시 파일(`config.json` / `.env` 연동) 적용 및 독립적인 설정 로딩 구조 구현
- **DoD-002**: `tests/` 테스트 수트에서 `127.0.0.1` / `localhost` 하드코딩 완전 제거 및 실행 플랫폼 동적 실 IP(`10.0.0.x` 대역 등) 감지 바인딩 적용
- **DoD-003**: `samples/common.py`에서 서버 패키지 내부 모듈 직접 의존성 제거 유지
- **DoD-004**: 전체 pytest 회귀 테스트 수트 (`uv run pytest`) 100% Green Pass 통과

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `samples/common.py`는 `samples/config.json`, `.env` 파일 또는 `SERVER_HOST` 환경변수를 파싱하여 훈련생이 서비스 플랫폼(`192.168.0.x`) 서버 주소를 손쉽게 명시/변경할 수 있는 기능을 제공해야 합니다.
- **FR-002**: `tests/` 회귀/통합 테스트 모듈은 `127.0.0.1` 및 `localhost` 호출을 일체 금지하며, `NetworkDetector`를 통해 현재 실행 플랫폼(`10.0.0.x` 등)의 실제 LAN IP를 동적으로 탐지하여 동일 네트워크 망 접속 가능 여부를 검증해야 합니다.
- **FR-003**: `samples/` 폴더에는 훈련생을 위한 `config.json` 설정 예시 파일이 제공되어야 합니다.

### Key Entities

- **SampleConfigLoader**: `samples/config.json` 및 `.env` 파일에서 서버 호스트 URL을 읽어오는 설정 로더
- **DynamicHostTestFixture**: 테스트 실행 플랫폼의 실 네트워크 IP를 동적으로 주입하는 pytest 피스처

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `samples/` 스크립트 실행 시 `config.json` 또는 `.env`를 통한 서버 주소 변경 지원 100%
- **SC-002**: `tests/` 테스트 코드 내 `127.0.0.1` / `localhost` 대상 검증 0건 (실 IP 전용 100%)
- **SC-003**: pytest 전체 회귀 테스트 통과율 100%

## Assumptions

- 개발 플랫폼 대역대는 `10.0.0.x`이며, 배포 대상 서비스 플랫폼 대역대는 `192.168.0.x`입니다.
- `samples/` 스크립트는 훈련생들이 클라이언트 환경에서 복사하여 사용할 수 있는 독립 스크립트 모음입니다.

