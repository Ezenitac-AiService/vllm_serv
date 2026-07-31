# Feature Specification: SQLite MetricsDB 손상 시 자동 격리 및 자가 복구 파이프라인 (066-metrics-db-auto-recovery)

**Feature Branch**: `066-metrics-db-auto-recovery`

**Created**: 2026-07-31

**Status**: Draft

**Input**: 레거시 서비스 플랫폼 환경 서버 셋팅/구동 시 `sqlite3.DatabaseError: database disk image is malformed` 발생으로 인한 서버 스타트업 서버 중단 방지 및 자동 데이터베이스 격리/복구 요구사항

## User Scenarios & Testing *(mandatory)*

### User Story 1 - SQLite 데이터베이스 손상(`malformed`) 감지 시 자동 격리 및 백업 복구 (`src/core/metrics_db.py`) (Priority: P1) 🎯 MVP

서버 관리자 및 시스템 운영자는 레거시 GPU 서버 환경에서 갑작스러운 비정상 종료나 디스크 오류로 인해 `data/metrics.db` 파일이 손상(`database disk image is malformed`)된 상태에서 서버를 셋팅하거나 실행할 때, 서버 서비스가 예외 트레이스백으로 치명적 구동 중단(`exit 1`)을 일으키지 않고 손상된 DB를 안전하게 격리(`data/metrics.db.corrupt_<timestamp>`)한 후 정상적인 새 메트릭 DB를 자동 초기화하여 서버가 즉시 정상 부팅되길 원합니다.

**Why this priority**: SQLite 데이터베이스 파일 손상 시 서버 스타트업 중단을 방지하고 서비스 가용성(High Availability) 및 장애 자가 치유(Auto-Healing)를 제공하는 최우선 장애 복구 요구사항입니다.

**Independent Test**: 고의로 손상된 SQLite 파일(`data/metrics.db`)을 작성한 후 `MetricsDB()`를 초기화할 때, 손상 파일이 격리되고 백그라운드 DB가 정상 복구되어 인퍼런스 메트릭 수집 및 API 조회가 정상적으로 수행되는지 독립 검증합니다.

**Acceptance Scenarios**:

1. **Given** `data/metrics.db` 파일이 손상된 상태일 때, **When** 서버 스타트업(`MetricsDB._init_db()`)이 실행되면, **Then** `sqlite3.DatabaseError` 또는 `DatabaseError: database disk image is malformed`를 감지하여 경고 로그를 출력하고, 손상 파일을 `data/metrics.db.corrupt_<timestamp>`로 백업 격리한 뒤 새로운 DB 연결 및 스키마를 자동 생성하여 부팅을 완수해야 합니다.
2. **Given** DB 격리 및 자가 복구가 완료된 후, **When** 메트릭 기록 및 조회 기능(`log_request()`, `get_summary()`)이 호출될 때, **Then** 예외 없이 정상 동작해야 합니다.

---

### User Story 2 - MetricsDB 손상 자가 복구 단위 테스트 및 통합 검증 (`tests/unit/test_metrics_db.py`) (Priority: P2)

QA 및 개발자는 단위 테스트 수트를 통해 손상된 DB 파일 주입 상황 및 권한 문제, 격리 이력 파일 생성을 자동으로 검증하여 추후 회귀 오류를 방지하길 원합니다.

**Why this priority**: DB 손상 복구 로직이 다양한 에러 유형(corrupt file, WAL file conflict, zero-byte file)에서도 신뢰할 수 있는지 자동 검증합니다.

**Independent Test**: `uv run pytest tests/unit/test_metrics_db.py` 실행 시 100% Green Pass 통과.

**Acceptance Scenarios**:

1. **Given** 헤더가 훼손된 임의의 손상된 `.db` 파일이 주입되었을 때, **When** `MetricsDB` 초기화를 수행하면, **Then** 자가 복구가 동작하여 새로운 `.db`가 초기화되고 기존 손상 파일은 타임스탬프 백업 파일로 보존되어야 합니다.

---

### Edge Cases

- `metrics.db-wal` 또는 `metrics.db-shm` 잔재 파일이 존재할 때 손상 격리 시 WAL 파일도 함께 동시 정리되는가?
- 디스크 용량 부족 또는 디렉터리 쓰기 권한 부재 시 복구 실패 로그를 명확히 출력하고 메모리 DB(`:memory:`)로 안전 Fallback 되는가?

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `src/core/metrics_db.py` 내 DB 연결 및 PRAGMA execution 시 `sqlite3.DatabaseError` 및 `sqlite3.OperationalError` 예외 포착 및 자동 백업 격리(`quarantine_corrupt_db()`) 및 재초기화 로직 구현
- **DoD-002**: `metrics.db-wal` 및 `metrics.db-shm` WAL 파일 동시 정리 보장
- **DoD-003**: `tests/unit/test_metrics_db.py` 내 malformed DB 주입 자가 복구 단위 테스트 작성 및 검증 통과
- **DoD-004**: 전체 pytest 회귀 테스트 수트(`uv run pytest`) 100% Green Pass 통과

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `src/core/metrics_db.py`는 데이터베이스 연결(`_get_connection()`) 또는 테이블 초기화(`_init_db()`) 중 `sqlite3.DatabaseError` (`database disk image is malformed` 포함) 또는 `sqlite3.OperationalError` 발생 시 이를 포착하여 복구 파이프라인을 트리거해야 합니다.
- **FR-002**: 손상 감지 시 기존 손상된 `metrics.db`, `metrics.db-wal`, `metrics.db-shm` 파일들을 `metrics.db.corrupt_<YYYYMMDD_HHMMSS>` 형식으로 안전하게 이동 격리(Quarantine)해야 합니다.
- **FR-003**: 격리 후 새로운 건강한 `metrics.db` 파일 및 테이블 스키마(`requests_metrics`, `daily_summaries`)를 자동으로 재창조 및 초기화하여 서버 시작 프로세스가 실패 없이 완수되도록 해야 합니다.
- **FR-004**: 파일 시스템 쓰기 거부 등 파일 기반 재창조가 불가능한 환경에서는 In-Memory 데이터베이스(`:memory:`)로 Fallback하여 서버 구동 중단을 차단해야 합니다.

### Key Entities

- **Metrics Database Connection**: SQLite3 DB (`data/metrics.db`, WAL 모드)
- **Quarantined Corrupt DB Archive**: `data/metrics.db.corrupt_20260731_080930`

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 손상된 `metrics.db` 주입 상황에서 서버 초기화 성공률 100% (`exit code 0`)
- **SC-002**: DB 자가 복구 소요 시간 < 500ms
- **SC-003**: 회귀 테스트 통과율 100%

## Assumptions

- 손상된 metrics DB의 기존 데이터는 복구 불가할 경우 백업 파일로 보존하고 신규 DB로 인스턴스를 즉시 교체함.
