# Quickstart Validation Guide: 서버 방화벽 구축 파이프라인 전수 검토 및 E2E 실측 테스트 (038-server-firewall-setup-pipeline)

본 가이드는 강화된 OS 방화벽 개방 검증 파이프라인과 서버 실물 IP 기반 Playwright E2E 대시보드 사용성 테스트를 시연 및 검증하기 위한 절차입니다.

---

## 1. 사전 준비 및 가상환경 동기화

```bash
# uv 가상환경 동기화
uv sync

# Playwright 브라우저 드라이버 동기화 (Playwright E2E 용)
uv run python -m playwright install --with-deps || true
```

---

## 2. 서버 구축 및 방화벽 파이프라인 시연

```bash
# 1. setup.sh 스크립트 실행을 통한 ufw 방화벽 상태 및 포트 개방 자동 진단 시연
./scripts/setup.sh

# 2. 백그라운드 서버 가동 및 방화벽 사전 점검(Pre-flight Check) 수행
./scripts/start_server.sh
```

---

## 3. 실물 IP 기반 네트워크 및 Playwright E2E 테스트 실행

```bash
# 실물 네트워크 소켓 및 Playwright E2E UI 테스트 실행 (127.0.0.1 루프백 대신 서버 실물 IP 10.0.0.41 실측)
REAL_NETWORK_TEST=1 uv run pytest tests/e2e/test_dashboard_e2e.py -v
```
