# Data Model & State Transitions: `077-sync-server-dashboard-lifecycle`

**Feature Directory**: [`specs/077-sync-server-dashboard-lifecycle`](file:///home/dev/storage/vllm_serv/specs/077-sync-server-dashboard-lifecycle)  
**Spec**: [`spec.md`](spec.md) | **Research**: [`research.md`](research.md)  

---

## 1. Entities & Schema

### ProcessControlState (프로세스 제어 상태 엔티티)

| Entity Attribute | Type | Description | Constraints |
|------------------|------|-------------|-------------|
| `daemon_name` | String | 데몬 식별자 (`main_server` / `dashboard_server`) | Required |
| `port` | Integer | 서비스 수신 포트 (`8081` / `8082`) | 1~65535 |
| `pid_file` | Path | PID 기록 파일 (`vllm_serv.pid` / `vllm_dashboard.pid`) | Absolute Path |
| `process_pattern` | String | `pgrep -f` 탐색 프로세스 실행 패턴 | Pattern string |
| `status` | Enum | `RUNNING`, `UNLOADED`, `ORPHANED`, `FAILED` | Required |
| `readiness_timeout_s` | Integer | 가동 대기 타임아웃 초 | Default 30 |

---

## 2. State Transition Diagram

```mermaid
stateDiagram-v2
    [*] --> UNLOADED : 초기 상태 (모든 포트/PID 해제)
    
    UNLOADED --> STARTING : ./start_server.sh 실행
    
    STARTING --> RUNNING : 8081 & 8082 30초 내 동시 Readiness 성공
    STARTING --> ATOMIC_ROLLBACK : 8081 또는 8082 중 1개라도 Readiness 실패
    
    ATOMIC_ROLLBACK --> UNLOADED : 양쪽 프로세스 SIGKILL 정리 & PID 파일 삭제 (Clean Exit)
    
    RUNNING --> STOPPING : ./stop_server.sh 실행
    ORPHANED --> STOPPING : ./stop_server.sh 실행 (단독 상주 좀비 정리)
    
    STOPPING --> UNLOADED : SIGTERM/SIGKILL 및 PID/VRAM 해제 완료
```
