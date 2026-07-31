# Implementation Plan: start_server.sh 데몬 구동시 PYTHONPATH 예외 및 0.0.0.0 curl 바인딩 오류 수정 (067-fix-server-startup-pythonpath)

**Branch**: `067-fix-server-startup-pythonpath` | **Date**: 2026-07-31 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/067-fix-server-startup-pythonpath/spec.md)

**Input**: Feature specification from `specs/067-fix-server-startup-pythonpath/spec.md`

## Summary

본 계획서는 타겟 서비스 서버에서 `./start_server.sh` 구동 시 발생했던 데몬 프로세스 사멸(`ModuleNotFoundError`) 및 `0.0.0.0` curl 헬스체크 연결 실패 문제를 수습하기 위해, `scripts/start_server.sh` 및 `scripts/status_server.sh` 구동 명령을 `uv run`으로 격리하고, `0.0.0.0` host를 `127.0.0.1` 루프백으로 자동 변환하며, `src/core/metrics_db.py` 내 `MetricsDB` 생성을 모듈 탑레벨 임포트 대신 지연 생성 싱글톤(Lazy Singleton Proxy)으로 전환하고 Fail-Fast 진단 출력을 보장하는 구현 계획을 정의합니다.

## Technical Context

**Language/Version**: Bash, Python 3.11+

**Primary Dependencies**: uv, curl, sqlite3, pytest

**Testing**: Pytest (`uv run pytest tests/unit/test_seed_pack_legacy.py`)

**Target Platform**: Linux Server (Legacy Service Platform)

**Project Type**: Infrastructure & Control Scripts Reliability

**Performance Goals**: 데몬 프로세스 구동 및 헬스체크 성공률 100%

**Constraints**: `uv run` 표준 준수 및 비파괴적 하위 호환성 유지

**Scale/Scope**: `scripts/start_server.sh`, `scripts/status_server.sh`, `src/core/metrics_db.py`, `tests/unit/test_seed_pack_legacy.py`

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
specs/067-fix-server-startup-pythonpath/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (/speckit-plan command output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── server-control-contract.json
└── checklists/
    └── requirements.md  # Specification quality checklist
```

### Source Code (repository root)

```text
scripts/
├── start_server.sh      # Updated background daemon launch script with uv run & Fail-Fast logging
├── status_server.sh     # Updated status script with 0.0.0.0 -> 127.0.0.1 curl conversion
└── make_seed_pack.sh    # Package verification for updated scripts

src/
└── core/
    └── metrics_db.py    # Converted to Lazy Singleton Proxy to eliminate top-level import crash

tests/
└── unit/
    └── test_seed_pack_legacy.py # Unit tests for control scripts and metrics_db lazy loading
```

**Structure Decision**: Standard repository layout modifying scripts, core modules, and unit tests.

## Complexity Tracking

*No violations.*
