# Data Model: uv sync Performance & Lockfile Entity Schemas

## Entities

### 1. EnvironmentSyncState (가상환경 동기화 상태 엔티티)

```json
{
  "lockfile_exists": true,
  "venv_exists": true,
  "sync_mode": "frozen | full | fallback",
  "execution_time_seconds": 0.8,
  "exit_code": 0
}
```

### 2. SetupPerformanceMetric (setup.sh 실행 성능 지표 엔티티)

```json
{
  "step": "2. uv 패키지 매니저 및 파이썬 가상환경 구성",
  "command": "uv sync --frozen",
  "target_latency_seconds": 2.0,
  "actual_latency_seconds": 0.8,
  "is_performance_met": true
}
```
