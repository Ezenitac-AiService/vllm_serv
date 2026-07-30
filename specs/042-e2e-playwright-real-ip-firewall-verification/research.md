# Phase 0 Research: 실할당 LAN IP 접속 및 Playwright E2E 브라우저 실측 검증 (042-e2e-playwright-real-ip-firewall-verification)

## Research Decisions

### 1. API 서버 네트워크 인터페이스 바인딩 (0.0.0.0 vs 127.0.0.1)
- **Decision**: `src/core/config_manager.py` 및 서버 런처에서 기본 바인딩 host를 `0.0.0.0`으로 설정/보장합니다.
- **Rationale**: `127.0.0.1`로 바인딩될 경우 루프백 인터페이스에서만 수신 대기하므로 방화벽 포트가 열려 있어도 외부 LAN IP(`10.0.0.41`)로 들어오는 신호가 `Connection Refused` 처리됩니다. `0.0.0.0` 바인딩 시 모든 NIC로 들어오는 연결을 올바르게 수신할 수 있습니다.

### 2. Playwright E2E 브라우저 실측 검증 수트 구축
- **Decision**: `tests/e2e/test_dashboard_playwright_real.py`를 작성하여 Playwright Headless Chromium으로 `http://10.0.0.41:8089/dashboard`에 실제 접속하고 DOM 요소 및 HTTP 200 OK 응답을 실측 검증합니다.
- **Rationale**: Anti-Mock 헌법 v1.4.0 원칙에 따라 목업 없이 실제 브라우저 엔진으로 네트워크/DOM 렌더링 수렴을 보장합니다.
