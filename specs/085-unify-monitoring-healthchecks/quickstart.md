# Quickstart Guide: 모니터링 정합성 검증 가이드

## 검증 시나리오

```bash
# 1. status_server.sh 구동 상태 확인
./status_server.sh
# 8082 대시보드 헬스체크 결과가 Port 8082 OPEN 으로 출력되는지 확인

# 2. diagnose_server_health.py 구동 상태 확인
uv run scripts/diagnose_server_health.py
# 8082 Port 8082_dashboard: ✅ OPEN 과 통일되는지 확인
```
