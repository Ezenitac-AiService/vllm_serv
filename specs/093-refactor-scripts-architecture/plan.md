# Implementation Plan: `scripts/` 디렉토리 스크립트 모듈화 및 결합도 완화 대대적 리팩토링 (`093-refactor-scripts-architecture`)

**Branch**: `093-refactor-scripts-architecture` | **Date**: 2026-08-04 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/093-refactor-scripts-architecture/spec.md)

**Input**: Feature specification from `/specs/093-refactor-scripts-architecture/spec.md`

## Summary

`scripts/` 하위 14개 전체 쉘/파이썬 스크립트의 외부 디렉토리(`src/`, `config/`, `data/`) 직결합 로직을 정밀 분석하여 하드코딩 참조를 제거하고, `scripts/common.sh` 공통 믹스인에 SRE 안전 래퍼(`try_optional_step`) 및 DevSecOps Cascade 포트 결정 믹스인(`get_configured_port()`)을 도입합니다. 또한 800줄 이상의 비대한 `setup.sh` 로직을 단일 책임 서브 모듈 스크립트로 분할하여 결합도를 낮추고 모듈화와 유지보수성을 극대화합니다.

## Technical Context

**Language/Version**: Python 3.11+, Bash Shell (POSIX compliant)

**Primary Dependencies**: `uv`, `pytest`

**Storage**: File system (`scripts/`, `config/`, `tests/`)

**Testing**: `pytest` (`uv run pytest tests/test_script_architecture.py`)

**Target Platform**: Linux server with NVIDIA CUDA GPU

**Project Type**: Infrastructure Shell Script Refactoring & Architecture Decoupling

**Performance Goals**: `setup.sh` 파이프라인 구동 속도 및 모듈 분할 후 오버헤드 < 0.1초

**Constraints**: 기존 CLI 명령어 인터페이스(`./setup.sh`, `./start_server.sh`, `./stop_server.sh`, `./status_server.sh`, `make_seed_pack.sh`) 100% 호환성 보존

**Scale/Scope**: `scripts/` 14개 스크립트 전체, `scripts/common.sh`, `tests/test_script_architecture.py`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_API_CALL=1) 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙)
- [x] 전체 회귀 테스트 수트 및 Playwright 기반 E2E 브라우저 실측 검증 계획이 포함되어 있는가? (의무적 회귀 테스트 및 브라우저 E2E 검증 원칙)

## Project Structure

### Documentation (this feature)

```text
specs/093-refactor-scripts-architecture/
├── plan.md              # 이 문서 (/speckit-plan 생성)
├── research.md          # Phase 0 기술 결정 및 Rationale
├── data-model.md        # Phase 1 도메인 엔티티 정의
├── quickstart.md        # Phase 1 검증 가이드
├── contracts/           # Phase 1 계약 명세
│   └── script_architecture_contract.json
└── tasks.md             # Phase 2 구현 작업 목록 (/speckit-tasks 생성 예정)
```

### Source Code (repository root)

```text
scripts/
├── common.sh            # [UPDATED] 공통 믹스인 (try_optional_step, get_configured_port, log_info)
├── setup.sh             # [REFACTORED] 모듈화 분할 및 결합도 완화 메인 셋업 스크립트
├── start_server.sh      # [REFACTORED] 믹스인 기반 포트 Cascade 및 하드코딩 제거 스크립트
├── stop_server.sh       # [REFACTORED] 안전 종료 믹스인 기반 스크립트
├── status_server.sh     # [REFACTORED] 포트/대시보드 실시간 점검 믹스인 스크립트
├── make_seed_pack.sh    # [REFACTORED] 마이그레이션 시드팩 아카이브 헬퍼
├── ensure_models.py     # [REFACTORED] 파라미터화된 필수 모델 다운로더
├── seed_db.py           # [REFACTORED] DB 초기화 파라미터 헬퍼
└── update_cuda_drivers.sh # [REFACTORED] SRE 안전 래퍼 연동 드라이버 헬퍼

tests/
└── test_script_architecture.py # [NEW] 스크립트 모듈화, 결합도 정적 스캔 및 호환성 테스트
```

**Structure Decision**: `scripts/common.sh`에 SRE 안전 래퍼 및 DevSecOps Cascade 포트 결정 믹스인을 집중 강화하고 각 제어 스크립트가 믹스인을 경유하도록 구성하는 깔끔한 아키텍처를 선택함.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | 위반 사항 없음 | N/A |
