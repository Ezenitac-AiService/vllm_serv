# Quickstart Guide: status_server.sh 대시보드 헬스체크 검증 가이드

**Feature Short Name**: `fix-dashboard-status-healthcheck`  
**Target Directory**: `specs/087-fix-dashboard-status-healthcheck/`  
**Date**: 2026-08-03  

---

## 1. 개요
본 가이드는 `./status_server.sh` 상태 확인 스크립트 실행 시 8082 웹 대시보드가 구동 중일 때 307 리다이렉트 추적을 통해 `🟢 대시보드 서비스 및 HTML DOM 정상 작동 중 (Port 8082 OPEN, DOM Verified)` 상태가 정확히 출력되는지 실측 검증하는 시나리오입니다.

---

## 2. 검증 시나리오 (Verification Scenarios)

### 시나리오 1: 대시보드 가동 상태에서의 status_server.sh 실측 점검
1. **서버 가동**:
   ```bash
   ./start_server.sh
   ```
2. **상태 조회 실행**:
   ```bash
   ./status_server.sh
   ```
3. **기대 결과**:
   - `[웹 대시보드 헬스체크 (http://127.0.0.1:8082/)]` 구역 아래에 `Port 8082 CLOSED`가 아닌 다음과 같이 초록색 정상 상태가 출력되어야 함:
   ```text
   🟢 대시보드 서비스 및 HTML DOM 정상 작동 중 (Port 8082 OPEN, DOM Verified)
   ```

### 시나리오 2: pytest 통합 회귀 테스트 실행
```bash
uv run pytest tests/integration/test_server_health_diagnostics_consistency.py -v
```
**기대 결과**: 모든 대시보드 헬스체크 진단 검증 테스트 100% Green Pass.
