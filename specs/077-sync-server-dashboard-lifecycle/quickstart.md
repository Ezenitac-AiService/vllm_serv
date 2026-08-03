# Quickstart Validation Guide: `077-sync-server-dashboard-lifecycle`

**Feature Directory**: [`specs/077-sync-server-dashboard-lifecycle`](file:///home/dev/storage/vllm_serv/specs/077-sync-server-dashboard-lifecycle)  
**Spec**: [`spec.md`](spec.md) | **Plan**: [`plan.md`](plan.md)  

---

## 1. Prerequisites

- Python 3.12, `uv` 패키지 매니저
- Bash 쉘 환경
- `uv run pytest` 테스트 실행 도구

---

## 2. Validation Scenarios (실측 검증 시나리오)

### Scenario 1: 원자적 동시 가동 검증 (`./start_server.sh`)

```bash
# 1. 기존 프로세스 종료
./stop_server.sh

# 2. 원스톱 구동 실행
./start_server.sh

# 3. PID 파일 및 포트 LISTEN 확인
ls -l vllm_serv.pid vllm_dashboard.pid
netstat -tulpn 2>/dev/null | grep -E "8081|8082" || ss -tulpn | grep -E "8081|8082"
```

**Expected Outcome**: 8081 포트와 8082 포트가 모두 LISTEN 상태로 수렴하고 `vllm_serv.pid`, `vllm_dashboard.pid` 파일이 모두 존재함.

---

### Scenario 2: 원자적 동시 완전 종료 및 VRAM 해제 검증 (`./stop_server.sh`)

```bash
# 1. 서버 안전 종료 실행
./stop_server.sh

# 2. 잔여 좀비 프로세스 감지 확인
pgrep -f "src.api.server" || echo "✓ Main Server Stopped"
pgrep -f "uvicorn src.api.main:app" || echo "✓ Dashboard Stopped"
pgrep -f "llama-server" || echo "✓ Llama Server Stopped"

# 3. PID 파일 삭제 확인
ls vllm_serv.pid vllm_dashboard.pid 2>/dev/null || echo "✓ All PID Files Cleaned"
```

**Expected Outcome**: `pgrep` 감지 프로세스 수 0건, PID 파일 존재하지 않음.

---

### Scenario 3: 독립 분리 상태 리포팅 검증 (`./status_server.sh`)

```bash
./status_server.sh
```

**Expected Outcome**: 8081 메인 서버 및 8082 대시보드 상태가 각각 명확히 분리된 라인으로 출력됨.

---

### Scenario 4: 회귀 테스트 수트 실행

```bash
uv run pytest tests/integration/test_dual_port_readiness.py tests/unit/test_shell_scripts.py
```

**Expected Outcome**: 모든 테스트 통과 (100% Green).
