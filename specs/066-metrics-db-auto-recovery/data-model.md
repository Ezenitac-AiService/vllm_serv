# Data Model: SQLite MetricsDB 손상 시 자동 격리 및 자가 복구 파이프라인 (066-metrics-db-auto-recovery)

**Feature**: `066-metrics-db-auto-recovery`

## Entities & Data Schemas

### 1. MetricsDB State Transition (`MetricsDBState`)

- **`HEALTHY`**: `data/metrics.db` 정상 동작 및 WAL 모드 활성화 상태
- **`CORRUPTED`**: `PRAGMA journal_mode=WAL;` 또는 테이블 생성 시 `DatabaseError: database disk image is malformed` 감지 상태
- **`QUARANTINED`**: 손상 파일이 `data/metrics.db.corrupt_<timestamp>`로 이동 완료된 상태
- **`RECREATED`**: 신규 `metrics.db` 파일 및 테이블 스키마 재창조 완료 상태
- **`IN_MEMORY_FALLBACK`**: 디스크 쓰기 오류 시 `:memory:` 샌드박스로 서빙 유지 상태

### 2. File Quarantine Mapping Scheme
- **`metrics.db`** ➡️ `metrics.db.corrupt_YYYYMMDD_HHMMSS`
- **`metrics.db-wal`** ➡️ `metrics.db-wal.corrupt_YYYYMMDD_HHMMSS`
- **`metrics.db-shm`** ➡️ `metrics.db-shm.corrupt_YYYYMMDD_HHMMSS`
