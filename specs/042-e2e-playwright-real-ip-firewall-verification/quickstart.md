# Quickstart: Playwright Real LAN IP E2E Validation (042-e2e-playwright-real-ip-firewall-verification)

---

## 1. 서버 구동 및 외부 IP 수신 대기 상태 확인

```bash
# 1. 서버 구동
./start_server.sh

# 2. 8089/8081 포트가 0.0.0.0으로 Listen 중인지 실측 확인
ss -tuln | grep -E "8081|8089"
# Expected Output: 0.0.0.0:8089, 0.0.0.0:8081
```

---

## 2. Playwright 브라우저 실측 E2E 테스트 구동

```bash
# Playwright 기반 real LAN IP 접속 및 UI DOM 렌더링 검증
uv run pytest tests/e2e/test_dashboard_playwright_real.py -v
```
