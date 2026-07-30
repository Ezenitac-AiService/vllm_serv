# Implementation Plan: setup.sh uv sync 속도 최적화 및 로컬 격리 고속화 (041-uv-sync-performance-fix)

**Branch**: `041-uv-sync-performance-fix` | **Date**: 2026-07-30 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/041-uv-sync-performance-fix/spec.md)

**Input**: Feature specification from `specs/041-uv-sync-performance-fix/spec.md`

## Summary

`scripts/setup.sh` Step 2의 `uv sync` 명령어를 `uv sync --frozen` 옵션 기반의 고속 수립 로직으로 전환합니다. 기존 `uv.lock` 및 `.venv`가 온전히 수립되어 있는 일반적인 배포/운영 환경에서 원격 PyPI 인덱스 재조회 지연을 스킵하여 Step 2 실행 시간을 2초 이내로 단축시키며, `set -e` 방어막(`if ! uv sync --frozen ...; then uv sync; fi`)을 수록하여 `uv.lock` 부재 또는 불일치 시 안전한 일반 `uv sync`로 Fallback합니다.

또한 `tests/unit/test_shell_scripts.py` 내의 `subprocess.run` 호출에 `timeout=15`를 적용하여 프로세스 멈춤(Hang)을 근본 방지합니다.

## Technical Context

**Language/Version**: POSIX Bash, Python 3.10+  
**Primary Dependencies**: uv package manager (v0.11+)  
**Storage**: File lock (`uv.lock`), Virtualenv (`.venv/`)  
**Testing**: pytest (`tests/unit/test_shell_scripts.py`)  
**Performance Goals**: `setup.sh` Step 2 소요 시간 <2초  
**Constraints**: 헌법 v1.4.0 (Strict `uv run`, Anti-Mock discipline, Non-destructive edits)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_API_CALL=1) 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙)

## Project Structure

### Documentation (this feature)

```text
specs/041-uv-sync-performance-fix/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Phase 0 research decisions
├── data-model.md        # Phase 1 entity & metric definitions
├── quickstart.md        # Phase 1 validation guide
└── checklists/
    └── requirements.md  # Requirements checklist (100% passing)
```

### Source Code (repository root)

```text
scripts/
└── setup.sh                 # Step 2 uv sync --frozen & Fallback implementation with subshell safety

tests/
└── unit/
    └── test_shell_scripts.py # Shell script performance, timeout=15 safety & fallback pytest cases
```

## Complexity Tracking

*No violations. All principles pass.*
