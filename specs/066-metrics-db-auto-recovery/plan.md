# Implementation Plan: SQLite MetricsDB 손상 시 자동 격리 및 자가 복구 파이프라인 (066-metrics-db-auto-recovery)

**Branch**: `066-metrics-db-auto-recovery` | **Date**: 2026-07-31 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/066-metrics-db-auto-recovery/spec.md)

**Input**: Feature specification from `specs/066-metrics-db-auto-recovery/spec.md`

## Summary

본 계획서는 레거시 서비스 플랫폼 셋팅 및 구동 시 발생한 `sqlite3.DatabaseError: database disk image is malformed` 오류를 근본적으로 해결하기 위해, `src/core/metrics_db.py` 내 DB 연결 및 초기화 단에서 손상 예외를 포착하여 기존 손상 파일(`metrics.db`, `.db-wal`, `.db-shm`)을 타임스탬프 파일로 자동 격리(Quarantine)하고 정상 신규 DB를 자동 재초기화(Auto-Healing)하는 예외 안전성 강화 계획을 정의합니다.

## Technical Context

**Language/Version**: Python 3.11+, sqlite3, pathlib, shutil

**Primary Dependencies**: sqlite3 (built-in standard library), pytest

**Storage**: Local SQLite3 Database (`data/metrics.db`, WAL Mode) with fallback to `:memory:`

**Testing**: Pytest (`uv run pytest tests/unit/test_metrics_db.py`)

**Target Platform**: Linux Server (Legacy Service Platform)

**Project Type**: Server Service Reliability & Exception Safety Infrastructure

**Performance Goals**: 자가 복구 처리 소요 시간 < 500ms, 서버 스타트업 성공률 100%

**Constraints**: 서버 구동 프로세스가 DB 손상으로 인해 `exit 1` 중단되지 않아야 함

**Scale/Scope**: `src/core/metrics_db.py` + `tests/unit/test_metrics_db.py`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_API_CALL=1) 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙)
- [x] 전체 회귀 테스트 수트 검증 계획이 포함되어 있는가? (의무적 회귀 테스트 원칙)

## Project Structure

### Documentation (this feature)

```text
specs/066-metrics-db-auto-recovery/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (/speckit-plan command output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── metrics-db-recovery-contract.json
└── checklists/
    └── requirements.md  # Specification quality checklist
```

### Source Code (repository root)

```text
src/
└── core/
    └── metrics_db.py    # Robust SQLite MetricsDB initialization with corrupt quarantine & auto-healing

tests/
└── unit/
    └── test_metrics_db.py # Unit test suite for corrupt DB quarantine and recovery
```

**Structure Decision**: Single project layout updating `src/core/metrics_db.py` and `tests/unit/test_metrics_db.py`.

## Complexity Tracking

*No violations.*
