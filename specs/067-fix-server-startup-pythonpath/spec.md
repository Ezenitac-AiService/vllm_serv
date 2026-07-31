# Feature Specification: start_server.sh 데몬 구동시 PYTHONPATH 예외 및 0.0.0.0 curl 바인딩 오류 수정 (067-fix-server-startup-pythonpath)

**Feature Branch**: `067-fix-server-startup-pythonpath`

**Created**: 2026-07-31

**Status**: Draft

**Input**: `./start_server.sh` 구동 후 `./status_server.sh` 실행 시 `프로세스 상태: ⚪ 중지됨 (UNLOADED)` 상태로 백그라운드 데몬이 즉시 종료되거나 헬스체크 대기 중 타임아웃이 발생하는 문제 해결 요구사항

## Clarifications

### Session 2026-07-31

- Q: MetricsDB 탑레벨 모듈 로딩 디스크 크래시 방지 및 데몬 구동 진단 강화 방안 → A: MetricsDB 지연 로딩 전환, start_server.sh uv run/curl 변환 및 데몬 실패 시 Fail-Fast 진단 로그 자동 출력을 명세에 통합 반영함.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - `start_server.sh` 구동 시 `PYTHONPATH` 보장 및 `uv run` 데몬 안정 구동 (Priority: P1) 🎯 MVP

서버 관리자는 시드팩을 압축 해제하고 `./setup.sh`를 완료한 후 `./start_server.sh`를 구동할 때, `src.api.server` 모듈 임포트 실패(`ModuleNotFoundError: No module named 'src'`)로 인해 백그라운드 프로세스가 즉시 사망하지 않고 `uv run python -m src.api.server` (또는 `PYTHONPATH=.`) 환경에서 백그라운드 데몬이 지속 실행되길 원합니다.

**Why this priority**: 백그라운드 데몬 프로세스가 구동 직후 사멸하지 않고 안정적으로 상주 서빙을 유지하기 위한 핵심 패치입니다.

**Independent Test**: `./start_server.sh` 실행 후 `./status_server.sh` 조회 시 `프로세스 상태: 🟢 구동 중 (RUNNING)` 및 PID 유지가 100% 정상 작동하는지 확인합니다.

**Acceptance Scenarios**:

1. **Given** `./start_server.sh` 스크립트를 실행할 때, **When** 백그라운드 데몬 구동 명령이 호출되면, **Then** `uv run python -m src.api.server` 또는 `PYTHONPATH`가 보장된 상태로 구동되어 `ModuleNotFoundError`로 인한 사멸이 없어야 합니다.
2. **Given** 서버 호스트 바인딩 주소가 `0.0.0.0`으로 설정된 경우, **When** `start_server.sh` 및 `status_server.sh`에서 헬스체크(`curl`)를 수행할 때, **Then** `0.0.0.0` 주소를 `127.0.0.1`로 적절히 변환하여 루프백 HTTP 헬스체크 응답을 성공적으로 수신해야 합니다.
3. **Given** 백그라운드 데몬 구동 중 타임아웃이나 프로세스 종료가 발생한 경우, **When** `start_server.sh` 대기가 종료될 때, **Then** `logs/server.log` 하단 15줄을 콘솔에 진단 정보로 즉시 출력(Fail-Fast Diagnostics)해야 합니다.

---

### User Story 2 - 서버 제어 스크립트 결합 검증 테스트 (`tests/unit/test_seed_pack_legacy.py`) (Priority: P2)

QA 및 개발자는 단위 테스트를 통해 `start_server.sh`, `status_server.sh`, `stop_server.sh` 스크립트 내부의 구동 명령어 및 `0.0.0.0` 바인딩 처리 로직을 검증하길 원합니다.

**Why this priority**: 자동화 테스트 수트를 통해 제어 스크립트 관련 결함을 사전 방지합니다.

**Independent Test**: `uv run pytest tests/unit/test_seed_pack_legacy.py` 실행 시 100% Green Pass 통과.

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `scripts/start_server.sh` 내 데몬 실행 명령을 `uv run python -m src.api.server` (또는 `PYTHONPATH` 명시)로 수정하여 모듈 임포트 사멸 차단
- **DoD-002**: `scripts/start_server.sh` 및 `scripts/status_server.sh` 내 `SERVER_HOST`가 `0.0.0.0`일 때 `CURL_HOST`를 `127.0.0.1`로 대체하여 HTTP 헬스체크 정상 수신
- **DoD-003**: `src/core/metrics_db.py` 내 `metrics_db` 지연 singleton 패턴(`get_metrics_db()`) 적용으로 탑레벨 모듈 로딩 시점의 디스크 I/O 크래시 원천 차단
- **DoD-004**: `tests/unit/test_seed_pack_legacy.py` 내 제어 스크립트 구동 명령 및 curl 호스트 변환 검증 테스트 추가
- **DoD-005**: 전체 pytest 회귀 테스트 수트 (`uv run pytest`) 100% Green Pass 통과

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `scripts/start_server.sh`는 `nohup setsid uv run python -m src.api.server < /dev/null > "$LOG_FILE" 2>&1 &` 형태로 백그라운드 프로세스를 가동하여 가상환경 격리 및 `PYTHONPATH` 임포트 경로를 보장해야 합니다.
- **FR-002**: `scripts/start_server.sh` 및 `scripts/status_server.sh`는 `SERVER_HOST` 파싱 결과가 `0.0.0.0`인 경우 `curl` 헬스체크 대상을 `127.0.0.1`로 수용하여 방화벽/루프백 접속 실패를 방지해야 합니다.
- **FR-003**: `scripts/make_seed_pack.sh` 실행 시 수정된 `start_server.sh` 및 `status_server.sh`가 시드팩에 바르게 패키징되어 배포 대상 서버에서도 동일하게 작동하도록 보장해야 합니다.
- **FR-004**: `src/core/metrics_db.py` 내 `MetricsDB` 생성을 모듈 탑레벨 임포트 시점 대신 지연 로딩/Safe Singleton(`get_metrics_db()`) 패턴으로 전환하여 모듈 import 시점의 파이썬 프로세스 크래시를 원천 차단해야 합니다.
- **FR-005**: `scripts/start_server.sh` 실행 중 헬스체크 실패 또는 백그라운드 프로세스 사멸 감지 시 `logs/server.log` 파일의 마지막 15줄을 콘솔에 진단 출력(Fail-Fast Diagnostics)해야 합니다.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `./start_server.sh` 구동 후 헬스체크 성공률 100%
- **SC-002**: `./status_server.sh` 프로세스 상태 `RUNNING` 100% 유지
- **SC-003**: 전체 pytest 회귀 테스트 통과율 100%
