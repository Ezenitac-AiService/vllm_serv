# Implementation Plan: 운영 쉘 스크립트 멀티 플랫폼 고도화

**Branch**: `021-enhance-shell-scripts` | **Date**: 2026-07-30 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/021-enhance-shell-scripts/spec.md)

**Input**: Feature specification from `/specs/021-enhance-shell-scripts/spec.md`

## Summary

운영 쉘 스크립트(`setup.sh`, `scripts/start_server.sh`, `scripts/stop_server.sh`, `scripts/status_server.sh`, `scripts/make_seed_pack.sh`)를 고도화하여 `020-cpu-build-detection`에서 구축된 CPU SIMD 명령어 감지, GPU Compute Capability 분석, 및 `config/platform_profiles.json` 프로필 매칭 로직을 완전히 활용하도록 개선한다. 이를 위해 `src/core/cpu_detector.py`에 `--match-profile` 및 `--check-preflight` CLI 옵션을 추가하고 쉘 스크립트 파이프라인에 통합한다.

## Technical Context

**Language/Version**: Python 3.10+ & Bash (POSIX compliant)

**Primary Dependencies**: `uv`, `llama-cpp-python`, `pytest`

**Storage**: `config/platform_profiles.json` (Local JSON file)

**Testing**: `pytest` (unit & integration tests for Python and shell scripts)

**Target Platform**: Linux x86_64 (Intel i7 930 Nehalem legacy & RTX 3060 dev workstation)

**Project Type**: Serving Infrastructure & Operational Shell Tooling

**Performance Goals**: `status_server.sh` 리포트 출력 5초 이내, `start_server.sh` 사전 점검 3초 이내 완료

**Constraints**: 파이썬 실행 및 테스트 시 `uv run` 사용 필수, GPU 하드웨어 미인식 시 fail-fast (CPU 폴백 금지)

**Scale/Scope**: 5개 핵심 운영 쉘 스크립트 고도화 및 `src/core/cpu_detector.py` CLI 확장

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책 준수)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (단위 테스트 및 통합 테스트 계획 수립)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (DoD-001~DoD-005 정의 완료)

## Project Structure

### Documentation (this feature)

```text
specs/021-enhance-shell-scripts/
├── spec.md              # Feature specification
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── contracts/           # Phase 1 output
    └── cli_contracts.md # CLI & shell exit code contracts
```

### Source Code (repository root)

```text
src/
└── core/
    ├── cpu_detector.py       # Added --match-profile & --check-preflight CLI options
    ├── config_manager.py     # Platform profile lookup utilities
    └── process_manager.py    # Native llama-server build integration

scripts/
├── make_seed_pack.sh         # Enhanced packaging with platform_profiles.json validation
├── start_server.sh          # Pre-flight check integration & fail-fast guide
├── status_server.sh         # Enhanced multi-platform hardware status report
└── stop_server.sh           # Clean process/VRAM cleanup

setup.sh                      # Integrated profile matching & CMAKE_ARGS propagation

tests/
├── unit/
│   ├── test_cpu_detector.py  # Unit tests for CLI flags & profile matching
│   └── test_shell_scripts.py # Unit/mock tests for shell script execution
└── integration/
    └── test_build_pipeline.py# End-to-end environment & build tests
```

**Structure Decision**: Single repository layout using `src/core/` for Python modules, `scripts/` and root `setup.sh` for operational shell scripts, and `tests/` for automated pytest suites.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A       | N/A        | No constitution violations present |
