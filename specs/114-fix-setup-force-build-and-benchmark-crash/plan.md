# Implementation Plan: setup.sh 강제 빌드 옵션(--force-build) 추가 및 benchmark_context_window NameError 크래시 수정 (Fix setup.sh Force Build & Benchmark Crash)

**Branch**: `114-fix-setup-force-build-and-benchmark-crash` | **Date**: 2026-08-08 | **Spec**: [specs/114-fix-setup-force-build-and-benchmark-crash/spec.md](spec.md)

**Input**: Feature specification from `/specs/114-fix-setup-force-build-and-benchmark-crash/spec.md`

## Summary

마이그레이션 대상 타겟 서버에서 발생하던 `scripts/benchmark_context_window.py`의 `NameError: name 'remaining_kv_budget' is not defined` 런타임 예외를 해결하고, `scripts/setup.sh`에 `--force-build` CLI 플래그 추가 및 `--wheel-path` 사용 시 기존 Fast-Track 캐시 오판을 스킵하여 CUDA 가속 휠이 `--force-reinstall` / `--no-cache-dir`로 원스톱 강제 설치되도록 보장합니다.

## Technical Context

**Language/Version**: Python 3.12, Bash (POSIX compliant)  
**Primary Dependencies**: `llama-cpp-python`, `uv`, `httpx`, `pytest`  
**Storage**: N/A (`config/server_config.json`, `config/model_context_profiles.json`)  
**Testing**: `pytest` (`tests/unit/`)  
**Target Platform**: Multi-platform Linux (Ubuntu, CentOS, Xeon/Core i7-930/Ryzen, GTX/RTX GPUs)  
**Project Type**: Python & Shell automation CLI / Core Service Infrastructure  
**Performance Goals**: Fast-track wheel installation <5s, force build execution clean failover  
**Constraints**: Zero regression, 100% Constitution v1.6.0 compliance  
**Scale/Scope**: 2 main files (`scripts/setup.sh`, `scripts/benchmark_context_window.py`) & unit test suites  

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
specs/114-fix-setup-force-build-and-benchmark-crash/
├── spec.md              # Feature specification with clarifications
├── plan.md              # Implementation plan (this file)
├── research.md          # Technical research & decisions (Phase 0)
├── data-model.md        # Options & state schemas (Phase 1)
├── quickstart.md        # Integration & verification guide (Phase 1)
└── checklists/
    └── requirements.md  # Specification quality checklist
```

### Source Code (repository root)

```text
scripts/
├── setup.sh                     # Added --force-build & bypass Fast-Track for --wheel-path
└── benchmark_context_window.py  # Fixed NameError for remaining_kv_budget

tests/
└── unit/
    ├── test_shell_scripts.py    # Unit tests for setup.sh CLI options & force build logic
    └── test_benchmark_context_window.py # Unit tests for benchmark_context_window safety
```

**Structure Decision**: Single project layout updating `scripts/` and `tests/unit/`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
