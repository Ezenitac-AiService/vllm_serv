# Feature Specification: status_server.sh 대시보드 헬스체크 307 리다이렉트 처리 및 상태 진단 정확도 정상화

**Feature Short Name**: `fix-dashboard-status-healthcheck`  
**Target Directory**: `specs/087-fix-dashboard-status-healthcheck/`  
**Status**: DRAFT  
**Date**: 2026-08-03  

---

## 1. 개요 및 원인 분석 리포트 (Overview & Root Cause Analysis)

### 1.1 현상 및 문제 상황
사용자가 `./status_server.sh` 상태 조회 스크립트를 실행했을 때, 8081 메인 서버와 8082 대시보드 프로세스(PID 2723090)가 정상 구동 중이고 `diagnose_server_health.py` 진단 결과 `Port 8082_dashboard: ✅ OPEN`으로 판명됨에도 불구하고, `./status_server.sh`의 웹 대시보드 헬스체크 구역에 다음과 같이 거짓 음성(False Negative) 오진이 출력됩니다:
```text
[서버 프로세스 및 서비스 상태]
8081 메인 서버 프로세스: 🟢 구동 중 (RUNNING, PID: 2723089)
8082 대시보드 프로세스  : 🟢 구동 중 (RUNNING, PID: 2723090)

[REST API 헬스체크 (http://127.0.0.1:8081/health)]
{
    "status": "alive",
    "pid": null
}

[웹 대시보드 헬스체크 (http://127.0.0.1:8082/)]
⚪ 대시보드 미구동 또는 포트 차단됨 (Port 8082 CLOSED)
```

### 1.2 실측 분석 기반 근거 (Empirical Log Evidence)
1. **HTTP 헤더 실측 데이터**:
   `curl -v http://127.0.0.1:8082/` 실측 수행 결과:
   ```text
   < HTTP/1.1 307 Temporary Redirect
   < location: /dashboard/
   < content-length: 0
   ```
   8082 포트의 루트 `/` 엔드포인트는 FastAPI/Uvicorn 대시보드 마운트 정책에 따라 `HTTP 307 Temporary Redirect` 응답(본문 0바이트)을 리턴합니다.
2. **스크립트 결함**:
   `scripts/status_server.sh` L78 코드 `DASH_HTML=$(curl -s "http://$CURL_HOST:8082/" || echo "")`는 `-L` (리다이렉트 추적) 옵션 없이 단순 GET 요청만 전송하여 0바이트 리다이렉트 본문(`""`)을 수신합니다.
3. **오진 판정 메커니즘**:
   수신된 본문이 빈 문자열이므로 DOM 키워드 검사 `grep -qE "vLLM|Dashboard|vllm_serv|대시보드"` 및 `[ -n "$DASH_HTML" ]` 검사를 모두 통과하지 못하고 `else` 블록으로 떨어져 `Port 8082 CLOSED`를 잘못 출력합니다.

---

## 2. 사용자 시나리오 및 테스트 (User Scenarios & Testing)

### US1: status_server.sh 대시보드 200 OK & 307 리다이렉트 정확 진단 (Priority: P1) 🎯 MVP
**운용자 관점**: 개발자 및 운용자는 `./status_server.sh` 실행 시 대시보드가 정상 구동 중일 때 307 리다이렉트를 올바르게 추적하여 `🟢 대시보드 서비스 및 HTML DOM 정상 작동 중 (Port 8082 OPEN, DOM Verified)` 결과를 확인해야 한다.

- **AC 1.1**: 대시보드가 8082 포트에서 구동 중일 때 `./status_server.sh` 실행 시 307 리다이렉트 및 `/dashboard/` 경로를 추적하여 HTML DOM 키워드 검증에 성공하고 `🟢 대시보드 서비스 및 HTML DOM 정상 작동 중` 메시지를 출력해야 한다.
- **AC 1.2**: 8082 포트 대시보드가 실제로 중지되었을 때만 `⚪ 대시보드 미구동 또는 포트 차단됨 (Port 8082 CLOSED)`을 출력해야 한다.

### US2: 다중 루프백 IP 및 /dashboard/ 직접 탐색 보장 (Priority: P1)
**운용자 관점**: `SERVER_HOST`가 `0.0.0.0` 또는 특정 바인딩 주소로 설정되어도 `127.0.0.1`, `localhost`, LAN IP 순서로 대시보드 헬스체크를 수행하여 네트워크 인터페이스 차이로 인한 오진을 방지해야 한다.

- **AC 2.1**: `status_server.sh` 및 관련 진단 스크립트는 `-L` 옵션을 포함한 `curl` 호출 및 `http://$HOST:8082/dashboard/` 직접 프로브를 수행해야 한다.

---

## 3. 작업 종료 조건 (Definition of Done)

- **DoD-001**: `./status_server.sh` 실행 시 8082 대시보드 구동 상태에서 `Port 8082 CLOSED` 오진이 발생하지 않고 `Port 8082 OPEN, DOM Verified`가 출력됨.
- **DoD-002**: `uv run pytest tests/integration/test_server_health_diagnostics_consistency.py` 회귀 테스트 100% 통과.

---

## 4. 기능 요구사항 (Functional Requirements)

- **FR-001 (Curl Location Follow & Direct Probe)**: `scripts/status_server.sh`는 포트 8082 대시보드 헬스체크 시 `curl -sL --max-time 3` 옵션을 사용하거나 `http://$CURL_HOST:8082/dashboard/` 경로를 포함하여 `HTTP 307 Temporary Redirect`에 대한 위치 추적을 보장해야 한다.
- **FR-002 (Multi-Probe & Network Binding Robustness)**: `SERVER_HOST`가 `0.0.0.0`인 경우 `127.0.0.1`, `localhost`, LAN IP 순으로 대시보드 포트 응답을 프로브하여 로컬 소켓 바인딩 특성에 의한 헬스체크 누락을 방지한다.
- **FR-003 (HTML DOM Keyword Verification)**: 획득한 HTML DOM에 `vLLM|Dashboard|vllm_serv|대시보드|Serving|Antigravity` 키워드가 포함되었는지 검증한다.
- **FR-004 (Integration Diagnostic Consistency)**: `tests/integration/test_server_health_diagnostics_consistency.py` 통합 회귀 테스트를 작성/갱신하여 `status_server.sh`와 `diagnose_server_health.py` 및 `test_dashboard_api.py` 간의 대시보드 진단 결과 일관성을 검증한다.

---

## 5. 성공 기준 (Success Criteria)

- **SC-001**: 대시보드 가동 상태에서 `./status_server.sh` 실행 시 `Port 8082 CLOSED` 거짓 음성(False Negative) 오진 발생률 0%.
- **SC-002**: `uv run pytest tests/integration/test_server_health_diagnostics_consistency.py` 100% Green Pass.

---

## 6. 프로젝트 헌법 준수사항 (Constitution Discipline)

- **헌법 I조 (한국어 작성)**: 모든 명세서, 가이드 및 보고서는 한국어로 작성.
- **헌법 II조 (Zero Mock)**: 가짜 하드코딩 응답을 금지하고 실제 8082 대시보드 Uvicorn 소켓 및 HTML 렌더링 응답을 실측 검증.
- **헌법 VII조 (의무적 회귀 테스트)**: `pytest` 회귀 테스트 수트 실행 및 검증 완료 필수.

---

## 7. 가정 사항 (Assumptions)

- 대시보드는 8082 포트에서 FastAPI/Uvicorn 서비스로 구동되며 `/` 경로 접근 시 `/dashboard/`로 307 리다이렉트하거나 직접 `/dashboard/`에서 HTML을 리턴함.
- `curl` 명령어가 서버 OS 환경에 기본 설치되어 있음.
