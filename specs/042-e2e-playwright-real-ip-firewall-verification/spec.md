# Feature Specification: 실할당 LAN IP 접속 및 Playwright E2E 브라우저 실측 검증 (042-e2e-playwright-real-ip-firewall-verification)

**Feature Branch**: `042-e2e-playwright-real-ip-firewall-verification`  
**Created**: 2026-07-30  
**Status**: Draft  
**Input**: User feedback: "이상한데, 서버 돌아가고 있었는데? -> benchmark_quality.py 실행 시 8081 포트 서버 프로세스를 재개시하는 과정에서 8089 포트 웹 대시보드가 자동 기동되지 않아 접속 불가 현상이 발생함."

---

## Clarifications

### Session 2026-07-30

- Q: Playwright E2E 브라우저 검증 수트 상세 동작 방식 → A: Option A - Headless Chromium으로 `http://10.0.0.41:8089/dashboard` 접속, DOM 요소 검증 및 화면 캡처(스크린샷) 증적 자동 저장
- Q: `start_server.sh` 및 벤치마크 후 8089 웹 대시보드 구동 상태 → A: 8081 포트 LLM 인퍼런스 서버 구동 시 포트 8089 웹 대시보드 서버(`src.api.server`)를 0.0.0.0으로 원자적 자동 동시 구동 보장
- Q: `benchmark_quality.py` 벤치마크 완료 후 복원 동작 → A: `finally` 구문에서 8081 LLM 서버 복원 후 포트 8089 웹 대시보드 API 서버가 정지 상태일 경우 자동 백그라운드 재시작 수록

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - real IP 기반 대시보드 접속 및 Playwright 브라우저 E2E 검증 (Priority: P1) 🎯 MVP

사용자가 `./start_server.sh`를 구동하거나 벤치마킹을 실행한 후 외부 동일 LAN 네트워크의 단말에서 실할당 IP (`http://10.0.0.41:8089/dashboard`)로 접속할 때, 8089 웹 대시보드가 `0.0.0.0` 호스트 바인딩으로 자동 백그라운드 구동되어 방화벽 차단 없이 브라우저 대시보드 화면이 100% 정상 렌더링되도록 보장하고 이를 Playwright 헤드리스 브라우저 테스트로 실측 입증합니다.

**Why this priority**: 벤치마킹 후 8089 웹 대시보드가 누락되어 접속 불능이 발생하는 현상을 방지하고, Anti-Mock 헌법에 따라 실제 브라우저 엔진으로 네트워크 통신 및 UI 렌더링을 100% 실측 입증합니다.

**Independent Test**: Playwright E2E 테스트(`pytest tests/e2e/test_dashboard_playwright_real.py`)를 실행하여 `http://10.0.0.41:8089/dashboard` 접속 후 DOM 요소(타이틀, 헬스 상태 카드) 렌더링 및 스크린샷 캡처 통과 검증.

**Acceptance Scenarios**:

1. **Given** vllm_serv `./start_server.sh` 구동 상태에서, **When** Playwright 브라우저가 외부 실할당 IP `http://10.0.0.41:8089/dashboard`에 접속하면, **Then** Connection Refused 또는 Timeout 없이 HTTP 200 OK와 함께 대시보드 DOM 요소가 정상 표출되며 증적 스크린샷이 저장된다.
2. **Given** `start_server.sh` 스크립트 또는 벤치마크가 완료되면, **When** API 서버가 바인딩되면, **Then** 8081 포트 LLM API와 8089 포트 웹 대시보드가 모두 `0.0.0.0` 호스트 주소로 자동 수신 대기(Listen)한다.

---

## Functional Requirements *(mandatory)*

- **FR-001**: API 서버(`src/api/server.py` & `src/core/config_manager.py`)의 기본 바인딩 호스트를 외부 접속이 가능한 `0.0.0.0`으로 설정/보장해야 한다.
- **FR-002**: `scripts/start_server.sh` 내에 8081 포트 LLM 인퍼런스 서버와 8089 포트 웹 대시보드 서버(`python3 -m src.api.server`)를 `0.0.0.0` 바인딩으로 원자적 자동 구동하는 로직을 수록해야 한다.
- **FR-003**: `scripts/benchmark_quality.py`의 `finally` 복원 구문에 8089 포트 웹 대시보드 서버 상태 검사 및 자동 백그라운드 재시작 방어막을 수록해야 한다.
- **FR-004**: `tests/e2e/test_dashboard_playwright_real.py` E2E 테스트 수트를 신규 작성하여 Playwright 브라우저 엔진으로 실할당 IP (`http://10.0.0.41:8089/dashboard`) 접속, DOM 요소 렌더링, 스크린샷 증적 캡처를 100% 실측 검증해야 한다.
- **FR-005**: Constitution v1.4.0 (Anti-Mock Discipline) 원칙에 따라 Playwright 브라우저 네트워크 응답 코드(HTTP 200) 및 실측 렌더링 캡처로 검증을 완납해야 한다.

---

## Success Criteria *(mandatory)*

- **SC-001**: Playwright E2E 테스트 수트(`pytest tests/e2e/test_dashboard_playwright_real.py`)가 `http://10.0.0.41:8089/dashboard` 접속 및 DOM/캡처 실측 시 100% 성공(PASS)한다.
- **SC-002**: 동일 LAN망 단말에서 `http://10.0.0.41:8089/dashboard` 접속 시 Connection Refused 오류 0건.
- **SC-003**: 벤치마크 구동 종료 후 `http://10.0.0.41:8089/dashboard` 대시보드 접속 가능 상태 유지.
- **SC-004**: 전체 pytest 단위 및 E2E 테스트 통과율 100% 달성.

---

## Key Entities *(optional)*

- **Playwright Browser Agent**: Chromium/WebKit 기반 헤드리스 E2E 테스트 브라우저.
- **Real Assigned LAN IP (`10.0.0.41`)**: 타깃 서버 호스트의 실제 물리 NIC IP 주소.
