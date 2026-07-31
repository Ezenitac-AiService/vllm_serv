# Feature Specification: 샘플 스크립트 실 IP 동적 자동 감지(192.168.0.x / 10.0.0.x / 듀얼 랜포트 지원) 및 연동 설정 개선

**Feature Branch**: `064-sample-scripts-real-ip`

**Created**: 2026-07-31

**Status**: Draft

**Input**: User description: "테스트 할때에 127.0.0.1 말고 실제 ip로 호출하는 내용으로, 우리 대상 플렛폼이 3개인데, 2종은 192.168.0.x 이고 1종은 10.0.0.x 야, 하드코딩하지 말고, ip 인식해야해, 게다가 1종은 듀얼랜포트라서 ip 감지를 단순하게 하면 안된다"

## Clarifications

### Session 2026-07-31

- Q: 타겟 플랫폼 3종 (192.168.0.x 2종, 10.0.0.x 1종 + 듀얼 랜포트) 환경에서 호스트 IP 인식 및 하드코딩 제거 방안 → A: 하드코딩 IP 주소를 전면 제거하고 `src/core/network_detector.py`의 `NetworkDetector.get_active_lan_ips()`를 활용하여 psutil 인터페이스 활성 상태(isup), 미할당/다운 포트, 링크-로컬(169.254.x.x) 및 루프백을 자동 필터링하고 실제 활성화된 유효 LAN IP(`192.168.0.x` 또는 `10.0.0.x`)를 동적으로 추출함. 명시적 환경변수 `SERVER_HOST` 지정 시 최우선 오버라이드 적용함.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 듀얼 랜포트 및 다중 서브넷(192.168.0.x / 10.0.0.x) 동적 IP 자동 감지 공통 헬퍼 (`samples/common.py`) (Priority: P1) 🎯 MVP

개발자 및 테스트 사용자는 `127.0.0.1` 및 특정 IP 하드코딩을 전면 제거하고, 3종 플랫폼(192.168.0.x 2종, 10.0.0.x 1종) 및 듀얼 랜포트 환경에서 미할당/다운 인터페이스를 필터링하여 실제 활성화된 호스트 LAN IP 주소를 동적으로 자동 탐지하는 공통 헬퍼 기능을 필요로 합니다.

**Why this priority**: 하드코딩 IP 의존성을 완전히 차단하여 3종 이기종 타겟 플랫폼 및 듀얼 포트 환경에서 샘플 스크립트가 무수정 자동 실행되도록 보장합니다.

**Independent Test**: `samples/common.py`의 `get_server_host()` 실행 시 듀얼 랜포트 중 활성화된 실제 유효 LAN IP(`192.168.0.x` 또는 `10.0.0.x`)를 리턴하는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** 10.0.0.x 대역 듀얼 랜포트 플랫폼(1개 포트 미연결/다운, 1개 포트 활성) 환경일 때, **When** `get_server_host()`를 호출하면, **Then** 미연결 포트 및 링크-로컬 주소를 제외하고 실제 구동 중인 10.0.0.x IP 호스트 주소(`http://10.0.0.x`)를 동적 반환해야 합니다.
2. **Given** 192.168.0.x 대역 플랫폼 환경일 때, **When** `get_server_host()`를 호출하면, **Then** 하드코딩 없이 감지된 `http://192.168.0.x` 호스트 주소를 반환해야 합니다.
3. **Given** 환경변수 `SERVER_HOST="http://192.168.0.99"` 지정 시, **When** `get_server_host()`를 호출하면, **Then** 동적 감지값보다 환경변수 지정 주소를 최우선으로 반환해야 합니다.

---

### User Story 2 - 전체 샘플 스크립트(`sample_01` ~ `sample_05`) 동적 실 IP 바인딩 전면 적용 (Priority: P2)

모든 예제 파이썬 스크립트(`sample_01_chat.py` ~ `sample_05_structured_output.py`)는 하드코딩된 IP를 제거하고 공통 헬퍼의 동적 실 IP 주소 기반으로 서버 포트(8081, 8090, 8091)에 접속하여 200 OK 응답을 받아야 합니다.

**Why this priority**: 사용자 요청대로 샘플 코드 사용자가 하드코딩 없이 자동 감지된 실 IP 주소 기반 연동 예제를 직접 확인하고 실행할 수 있도록 보장합니다.

**Independent Test**: `uv run python samples/sample_01_chat.py` 실행 시 자동 감지된 호스트 IP로 성공적으로 API 요청을 전송하고 텍스트 결과를 출력하는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** 8081/8090/8091 서빙 포트 구동 중일 때, **When** `sample_01` ~ `sample_05` 스크립트를 각각 실행하면, **Then** 동적 실 IP 엔드포인트를 호출하여 예외 없이 정상 응답을 반환해야 합니다.

---

### User Story 3 - 단위/통합 회귀 테스트 수트 동적 IP 감지 검증 (Priority: P3)

QA 및 개발자는 회귀 테스트 수트 (`tests/unit/test_sample_scripts.py`) 및 네트워크 감지 테스트(`tests/unit/test_network_detector.py`)가 듀얼 랜포트 오매칭 필터링 및 동적 IP 감지를 포함하여 100% 통과하는지 검증해야 합니다.

**Why this priority**: 듀얼 랜포트 미할당 포트 오매칭 방지 및 회귀 테스트 신뢰성을 보장합니다.

**Independent Test**: `uv run pytest tests/unit/test_sample_scripts.py tests/unit/test_network_detector.py` 실행 시 100% Green Pass 통과.

**Acceptance Scenarios**:

1. **Given** 테스트 수트 실행 시, **When** `uv run pytest`가 수행되면, **Then** 듀얼 랜포트 환경 필터링 및 동적 IP 호환성 테스트가 성공해야 합니다.

---

### Edge Cases

- 듀얼 랜포트 중 1개 포트의 케이블이 뽑혀 있거나 IP가 미할당(`169.254.x.x` 또는 down) 상태일 때 `NetworkDetector`가 이를 정확히 스킵하고 유효 활성 포트를 선택하는가?
- 오프라인 루프백 단독 환경 시 `127.0.0.1`로 안전하게 폴백되는가?

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `samples/common.py`에 하드코딩 없는 동적 LAN IP 감지(`NetworkDetector.get_active_lan_ips()`) 및 `SERVER_HOST` 환경변수 우선 적용 구현
- **DoD-002**: 듀얼 랜포트(미할당/다운 포트 및 링크-로컬 169.254.x.x 스킵) 호환성 검증 및 3종 타겟 플랫폼(192.168.0.x / 10.0.0.x) 자동 지원
- **DoD-003**: `sample_01_chat.py` ~ `sample_05_structured_output.py` 5개 샘플 파일 하드코딩 IP 전면 제거 및 동적 호스트 적용
- **DoD-004**: 전체 pytest 회귀 테스트 수트(`uv run pytest`) 100% Green Pass 통과

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 시스템은 `samples/common.py`에 `get_server_host()` 함수를 제공하여 `SERVER_HOST` 환경변수를 최우선 확인하고, 미설정 시 `NetworkDetector.get_active_lan_ips()`를 통해 듀얼 랜포트의 활성 포트에서 추출된 실 IP(`192.168.0.x` 또는 `10.0.0.x`)를 동적 구성해야 합니다.
- **FR-002**: `NetworkDetector`는 psutil/socket 기반 인터페이스 스캔 시 듀얼 랜포트 중 다운 상태(`isup == False`), IP 미할당, 링크-로컬(`169.254.x.x`), 루프백(`127.0.0.1`) 주소를 엄격히 제외하고 유효 LAN IPv4 주소를 반환해야 합니다.
- **FR-003**: `sample_01_chat.py` ~ `sample_05_structured_output.py` 5개 샘플 파일은 하드코딩된 IP를 사용하지 않고 `get_server_host()`를 통해 동적 감지된 호스트 IP로 서빙 포트(8081, 8090, 8091)를 호출해야 합니다.

### Key Entities

- **Dynamic Network Detector**: `NetworkDetector` 클래스 기반 듀얼 포트 감지 및 유효 LAN IPv4 자동 선택 객체

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 하드코딩 0건 및 동적 탐지된 실 IP 호스트를 통한 5개 샘플 스크립트 실행 응답 성공률 100%
- **SC-002**: 듀얼 랜포트 미할당 포트 필터링 검증 및 전체 pytest 회귀 테스트 수트 통과율 100%

## Assumptions

- 3종 플랫폼 환경 중 활성화된 네트워크 인터페이스가 유효한 IPv4 주소(192.168.0.x 또는 10.0.0.x)를 소유함.
- `psutil` 라이브러리가 설치되어 네트워크 인터페이스 플래그(`isup`) 감지가 가능함.
