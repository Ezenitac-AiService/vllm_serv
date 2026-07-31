# Research: SQLite MetricsDB 손상 시 자동 격리 및 자가 복구 파이프라인 (066-metrics-db-auto-recovery)

**Feature**: `066-metrics-db-auto-recovery`

## Technical Decisions & Rationale

### Decision 1: `MetricsDB` 초기화 시 `sqlite3.DatabaseError` / `OperationalError` 전역 캐칭 및 격리 메서드 구축
- **선택된 방식**: `src/core/metrics_db.py`의 `MetricsDB.__init__()`, `_get_connection()`, `_init_db()` 구간에서 `sqlite3.DatabaseError` 또는 `sqlite3.OperationalError` 예외 발생 시 이를 포착하여 `quarantine_and_recreate_db()` 메서드를 호출함.
- **이유**: `conn.execute("PRAGMA journal_mode=WAL;")` 실행 시 DB 파일 헤더나 인덱스가 훼손된 경우 `sqlite3.DatabaseError: database disk image is malformed`가 발생합니다. 이 예외를 무시하거나 전락시키지 않고 즉시 포착하여 복구 파이프라인을 구동함으로써 서버 스타트업 중단을 100% 방지합니다.
- **대안 검토**: 수동으로 DB 파일 삭제 안내 로그만 남기고 `exit(1)` 처리 — 사용자의 개입이 필요하므로 서버 자동 시드/부팅(Auto-Healing) 원칙에 위배되어 기각함.

### Decision 2: 격리 백업(Quarantine) 및 WAL/SHM 파일 동시 정리
- **선택된 방식**: 손상된 `metrics.db`뿐만 아니라 잔재하는 `metrics.db-wal` 및 `metrics.db-shm` 파일이 존재할 경우, 동일한 타임스탬프(`metrics.db.corrupt_<YYYYMMDD_HHMMSS>`)로 안전하게 격리 이동시킴.
- **이유**: WAL(Write-Ahead Logging) 모드에서는 `.db-wal` 파일 손상 시에도 동일한 `malformed` 에러가 재발할 수 있으므로 관련 보조 파일 전체를 함께 격리해야 새 DB 초기화가 깨끗하게 완수됩니다.

### Decision 3: 인메모리 Fallback (`:memory:`) 안전 장치
- **선택된 방식**: 디스크 권한 문제나 IO 장애로 새 DB 파일 격리/재생성이 실패할 경우 `sqlite3.connect(":memory:")`로 인메모리 Fallback 처리함.
- **이유**: 어떤 디스크 결함 환경에서도 인퍼런스 서버 메인 API 부팅이 절대 중단되지 않도록 보장합니다.
