# Feature Specification: setup.sh uv sync 속도 최적화 및 로컬 격리 고속화 (041-uv-sync-performance-fix)

**Feature Branch**: `041-uv-sync-performance-fix`  
**Created**: 2026-07-30  
**Status**: Draft  
**Input**: User report: "setup.sh 구동 시 uv sync 과정에서 너무 오랫동안 대기하는 지연 문제 발생. uv sync는 이렇게 오래 걸리는 작업이 아니어야 함."

---

## Clarifications

### Session 2026-07-30

- Q: 최초 설치 환경(uv.lock 또는 .venv 부재 시)에서의 uv sync 처리 전략 → A: `uv.lock` 및 `.venv` 유효 시 `uv sync --frozen` (고속 모드), 부재 시 일반 `uv sync` (자동 Fallback)
- Q: 다중 페르소나 비판론자 보완 항목 → A: `set -e` 터미널 즉시 종료 방지를 위한 파이프라인 방어막(`if ! uv sync --frozen ...`) 구축 및 pytest `timeout=15` 타임아웃 격리 보장

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - setup.sh uv sync 즉시 통과 및 오프라인/고속 동기화 (Priority: P1) 🎯 MVP

사용자가 `./scripts/setup.sh`를 실행할 때, 이미 설치된 파이썬 가상환경(`.venv`) 및 lockfile이 존재하는 경우 `uv sync` 단계에서 원격 인덱스 인덱싱이나 불필요한 의존성 재해석 없이 1~2초 이내에 동기화가 즉시 완납되도록 보장합니다.

**Why this priority**: 반복적인 setup.sh 구동 시 가상환경 준비 단계에서 수십 초의 무의미한 네트워크/디스크 지연이 발생하는 문제를 제거하여 개발 생산성과 체감 속도를 크게 향상시킵니다.

**Independent Test**: `.venv`와 `uv.lock`이 생성되어 있는 상태에서 `./scripts/setup.sh` 실행 시 Step 2 `uv sync` 구간이 2초 이내에 통과하는지 실측 검증.

**Acceptance Scenarios**:

1. **Given** `uv.lock` 및 `.venv`가 존재하는 환경에서, **When** `./scripts/setup.sh`를 구동하면, **Then** `uv sync --frozen` 옵션으로 실행되어 네트워크 재조회 없이 2초 이내에 완료된다.
2. **Given** 최초 설치 서버 환경이거나 `uv.lock`이 없는 경우, **When** `setup.sh`를 실행하면, **Then** `uv sync --frozen` 시도 후 일반 `uv sync`로 자동 Fallback되어 가상환경 구성을 완납한다.
3. **Given** 오프라인 환경 또는 원격 PyPI 인덱스 응답이 느린 상황에서, **When** `setup.sh`를 실행하면, **Then** 오프라인/고속 동기화 모드로 동작하여 렌더링 블로킹이나 타임아웃 지연이 발생하지 않는다.

---

### User Story 2 - uv sync 실행 상태 및 진행 시간 투명 로깅 (Priority: P2)

`uv sync` 실행 시 사용자가 현재 무슨 작업이 진행 중인지 인지할 수 있도록 명확한 로깅 문구와 빠른 바이패스 안내 메시지를 제공합니다.

**Why this priority**: 진행 상황을 알 수 없어 먹통(Hang)된 것처럼 보이는 착시를 방지하고 투명성을 제공합니다.

**Independent Test**: `./scripts/setup.sh` 구동 시 `uv sync` 진입 메시지와 Fast-Track 완납 로그가 터미널에 선명하게 출력되는지 확인.

**Acceptance Scenarios**:

1. **Given** `setup.sh` 구동 시, **When** Step 2 가상환경 동기화에 진입하면, **Then** "[SETUP INFO] 가상환경 고속 동기화 중 (uv sync --frozen)..." 메시지가 출력된다.

---

## Functional Requirements *(mandatory)*

- **FR-001**: `scripts/setup.sh` 내 `uv sync` 구문 실행 시 우선 `uv sync --frozen`으로 수행하여 `uv.lock` 변경 없는 상태에서의 원격 인덱스 재검색 지연을 차단해야 한다.
- **FR-002**: 기존 가상환경(.venv)이 존재하고 의존성 패키지가 충족된 경우 `uv sync` 단계를 고속 검증 모드로 처리하여 2초 이내 구동 완납을 보장해야 한다.
- **FR-003**: `uv.lock` 불일치 또는 미존재 시 `set -e` 스크립트 중단을 방지하기 위해 `if ! uv sync --frozen 2>/dev/null; then uv sync; fi` 파이프라인 안전 방어막을 구축해야 한다.
- **FR-004**: 테스트 멈춤(Hang)을 방지하기 위해 `tests/unit/test_shell_scripts.py` 내 모든 `subprocess.run` 구문에 `timeout=15` 및 예외 처리 구문을 의무 수록해야 한다.
- **FR-005**: Constitution v1.4.0 (Anti-Mock Discipline) 준수를 위해 실측 실행 시간(time ./scripts/setup.sh)을 측정하고 단위/통합 테스트 수트로 수렴을 입증해야 한다.

---

## Success Criteria *(mandatory)*

- **SC-001**: 기존 `.venv` 및 `uv.lock` 환경에서 `setup.sh` Step 2 `uv sync` 구간 실행 소요 시간이 **2초 이내**로 단축된다.
- **SC-002**: 인터넷 연결이 차단된 오프라인 환경에서도 `setup.sh`가 네트워크 에러 없이 정상적으로 파이썬 환경 검증을 마치고 완납된다.
- **SC-003**: pytest 테스트 수트 실행 시 멈춤 현상 없이 100% 통과율을 유지한다.

---

## Key Entities *(optional)*

- **Lockfile (`uv.lock`)**: 프로젝트 파이썬 의존성 패키지의 정확한 버전 락 정보.
- **Virtual Environment (`.venv/`)**: 현지 가상 파이썬 런타임 패키지 디렉토리.
