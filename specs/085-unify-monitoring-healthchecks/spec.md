# Feature Specification: 서버 현황 모니터링(status_server.sh vs diagnose_server_health.py) 불일치 해소 및 헬스체크 통일

**Feature Short Name**: `unify-monitoring-healthchecks`  
**Target Directory**: `specs/085-unify-monitoring-healthchecks/`  
**Status**: DRAFT  
**Date**: 2026-08-03  

---

## 1. 개요 및 원인 분석 리포트 (Overview & Problem Statement)

### 1.1 모니터링 결과 불일치 현상
서버가 구동 중인 상태에서 현황 점검 도구를 실행했을 때, 두 스크립트가 8082 대시보드 상태에 대해 서로 모순되는 결과를 출력하고 있습니다:

1. **`./status_server.sh` 출력**:
   - `8082 대시보드 프로세스: 🟢 구동 중 (RUNNING, PID: 2656302)`
   - `[웹 대시보드 헬스체크 (http://127.0.0.1:8082/)]` -> **`⚪ 대시보드 미구동 또는 포트 차단됨 (Port 8082 CLOSED)`**
2. **`uv run scripts/diagnose_server_health.py` 출력**:
   - `[방화벽 및 포트 개방 상태]` -> **`Port 8082_dashboard: ✅ OPEN`**
   - `🖥️ 웹 대시보드 E2E 렌더링 : ✅ ON`
   - `STATUS: 🎉 SYSTEM HEALTHY`

### 1.2 불일치 발생 원인 분석 (Root Cause)
- `./status_server.sh`는 `127.0.0.1:8082` 단일 주소에 대한 `curl` 호출 실패 시 무조건 `Port 8082 CLOSED`로 표시합니다.
- Uvicorn 대시보드(`src/api/main.py`)가 `0.0.0.0:8082` 바인딩 시 `127.0.0.1` 루프백 응답 지연이나 타임아웃(curl timeout 설정 미비)으로 실패할 수 있으며, LAN IP(`10.0.0.41`) 탐지 폴백이 모니터링 쉘 스크립트에 누락되어 있었습니다.
- 반면 `diagnose_server_health.py`는 LAN IP(`10.0.0.41`) 탐색 및 다중 루프백 IP(`127.0.0.1`, `localhost`, `10.0.0.41`) 검증을 수행하여 정상 Open을 감지했습니다.

---

## 2. 사용자 시나리오 및 수용 기준 (User Stories & Acceptance Criteria)

### US1: 모니터링 진단 도구 간 헬스체크 결과 100% 일치 (Priority: P1) 🎯 MVP
**사용자 관점**: 개발자 및 운용자는 `./status_server.sh`와 `diagnose_server_health.py` 중 어떤 도구를 실행하더라도 동일한 서버 및 대시보드 개방 상태를 확인받아야 한다.

- **AC 1.1**: 대시보드가 정상 구동 중일 때 `./status_server.sh` 조회 결과가 `⚪ 대시보드 미구동` 대신 `🟢 대시보드 정상 동작 중 (Port 8082 OPEN)`을 출력해야 한다.
- **AC 1.2**: `./status_server.sh`와 `diagnose_server_health.py` 간 포트 8081 및 포트 8082의 개방 상태 판정 결과가 상충되지 않아야 한다.

### US2: 쉘 스크립트 상의 다중 IP 및 소켓 검증 강화 (Priority: P1)
**사용자 관점**: 네트워크 인터페이스가 LAN IP(`10.0.0.41`)에 바인딩된 경우에도 쉘 스크립트가 헬스체크에 성공해야 한다.

- **AC 2.1**: `status_server.sh`는 `127.0.0.1`뿐만 아니라 자동 감지된 LAN IP(`10.0.0.41`) 및 `fuser`/`ss`/`lsof` 소켓 존재 여부를 종합 평가하여 최종 상태를 판정한다.
- **AC 2.2**: `curl` 타임스탬프 및 타임아웃 인자를 정밀하게 추가하여 오탐(False Negative)을 방지한다.

---

## 3. 기능 요구사항 (Functional Requirements)

- **FR-001**: `scripts/status_server.sh`의 대시보드 HTTP 헬스체크 로직을 고도화하여, `127.0.0.1:8082`, `localhost:8082`, 유효 LAN IP(`10.0.0.41:8082`) 다중 프로브 탐색 및 `ss -tulpn`/`lsof -i:8082` 소켓 점유 검증을 수행하도록 수정한다.
- **FR-002**: `scripts/diagnose_server_health.py`와 `scripts/status_server.sh`가 공유하는 탐색 대상 IP 및 포트 헬스체크 규칙을 통일한다.
- **FR-003**: 대시보드 HTTP GET 프로브 실패 시 단순 문자열 출력이 아닌 HTTP 응답 코드 및 바인딩 상태를 정확히 디버그 문맥으로 제공한다.
- **FR-004**: 통합 테스트 수트(`tests/integration/test_server_health_diagnostics.py`)에 `status_server.sh` 및 `diagnose_server_health.py` 정합성 검증 테스트를 작성한다.

---

## 4. 성공 기준 (Success Criteria)

- **SC-001**: `./status_server.sh` 및 `uv run scripts/diagnose_server_health.py` 동시 실행 시 8081/8082 포트 헬스체크 상태 100% 일치 (둘 다 `Port 8082 OPEN` 및 `HTTP 200 OK`).
- **SC-002**: LAN IP(`10.0.0.41`) 환경에서 `./status_server.sh` 오탐 0건 달성.

---

## 5. 프로젝트 헌법 준수사항 (Constitution Discipline)

- **헌법 I조 (한국어 문서화)**: 명세서 및 품질 보고서는 한국어로 작성.
- **헌법 II조 (Zero Mock)**: 가짜 성공 및 불투명 예외 우회를 금지하고 실제 프로세스 소켓 및 네트워크 프로브를 통해 상태를 명시함.
