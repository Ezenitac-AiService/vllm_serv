# Implementation Plan: Seed Pack Wheel Validation & Setup Failure Diagnostics (시드 팩 사전 빌드 휠 정밀 검증 기반 재빌드 및 Fast-Track 진단 강화)

**Branch**: `035-seed-pack-wheel-diagnostics` | **Date**: 2026-07-30 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/035-seed-pack-wheel-diagnostics/spec.md)

**Input**: Feature specification from `/specs/035-seed-pack-wheel-diagnostics/spec.md`

## Summary

`make_seed_pack.sh` 실행 시 기존 `wheels/legacy_i7_930/*.whl` 사전 빌드 휠을 무조건 삭제하지 않고 파이썬 내장 스캐너(`scripts/verify_wheel_binary.py`)로 `.so` 파일의 AVX 유입 여부(0개) 및 CUDA 수용성을 정밀 검증합니다. 정상 휠은 0초 만에 재사용하고 오염 휠 감지 시 자동 삭제 후 `-DGGML_AVX=OFF` 인자로 새로 빌드합니다. 또한 `setup.sh` 구동 시 Fast-Track 실패 상황에서 `2>/dev/null` 에러 은폐를 완전히 제거하고 1줄 요약 진단 사유 및 파이썬 stderr Traceback을 100% 표출하도록 개선합니다.

## Technical Context

**Language/Version**: Python 3.10+ / Bash Shell

**Primary Dependencies**: `zipfile`, `struct`, `pytest`

**Storage**: N/A (Build artifacts in `wheels/legacy_i7_930/`)

**Testing**: `pytest` (`uv run pytest`)

**Target Platform**: Linux Server (i7-930 Nehalem CPU & GTX 1070 GPU)

**Project Type**: Infrastructure Shell Scripts & Build Tooling

**Performance Goals**: 휠 검증 완료 < 1초, 정상 휠 감지 시 C++ 재컴파일시간 0초

**Constraints**: `uv run` 환경 지원, 파이썬 순수 내장 모듈 사용(외부 `objdump` 도구 의존성 배제)

**Scale/Scope**: `scripts/make_seed_pack.sh`, `scripts/setup.sh`, `scripts/verify_wheel_binary.py`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙)

## Project Structure

### Documentation (this feature)

```text
specs/035-seed-pack-wheel-diagnostics/
├── plan.md              # Implementation Plan
├── research.md          # Phase 0 Research
├── data-model.md        # Phase 1 Data Model
├── quickstart.md        # Phase 1 Quickstart Validation Guide
└── contracts/
    └── wheel_scanner.md # Contract Specification
```

### Source Code (repository root)

```text
scripts/
├── make_seed_pack.sh          # Seed pack creation with conditional wheel rebuild
├── setup.sh                   # Environment setup with transparent fast-track failure diagnostics
└── verify_wheel_binary.py     # Pure-python binary scanner verifying 0 AVX instrs

tests/
├── unit/
│   ├── test_seed_pack_legacy.py # Unit tests for seed pack wheel verification & rebuild
│   └── test_shell_scripts.py    # Unit tests for setup.sh diagnostic logging
```

**Structure Decision**: Option 1 (Single project shell script & python utility structure).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*(해당 사항 없음 - 헌장 원칙 100% 준수)*
