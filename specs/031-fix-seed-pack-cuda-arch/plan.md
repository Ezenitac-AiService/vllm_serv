# Implementation Plan: i7-930/GTX 1070 타겟 시드 팩 사전 빌드 휠 CMAKE_CUDA_ARCHITECTURES 명시 및 고속 복원 검증 통과 (031-fix-seed-pack-cuda-arch)

**Branch**: `031-fix-seed-pack-cuda-arch` | **Date**: 2026-07-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/031-fix-seed-pack-cuda-arch/spec.md`

## Summary

`scripts/make_seed_pack.sh` 스크립트를 업데이트하여 i7-930 전용 휠 컴파일 시 `FORCE_CMAKE=1` 환경변수와 `CMAKE_ARGS="-DGGML_CUDA=ON -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_F16C=OFF -DGGML_FMA=OFF -DGGML_NATIVE=OFF -DCMAKE_CUDA_ARCHITECTURES=61"` 플래그를 추가합니다.

이를 통해 타겟 머신(GTX 1070, sm_61)에 대한 CUDA 아키텍처 바이너리 수록과 호스트 CPU 명령어 세트 누출(`-march=native`) 억제를 완벽히 보장하여, 시드 팩 복원 후 `setup.sh` 구동 시 `llama_supports_gpu_offload()` 검증이 100% 통과하고 C++ 소스 재컴파일 없는 Fast-Track 주입(<5초)을 달성합니다.

## Technical Context

**Language/Version**: Python 3.12+, Bash Shell Scripting (`set -eo pipefail`)

**Primary Dependencies**: `uv`, `llama-cpp-python` (with CUDA GGML backend)

**Storage**: Local files (`wheels/legacy_i7_930/`, `dist/vllm_serv_seed.tar.gz`)

**Testing**: `pytest`, Bash script syntax & compilation option unit tests (`tests/unit/test_seed_pack_legacy.py`)

**Target Platform**: Linux (Ubuntu 24.04 LTS), Platform C (`legacy-i7-930-gtx1070`)

**Project Type**: Server Deployment Pipeline & Seed Pack CLI Tool

**Performance Goals**: i7-930 머신 시드 팩 주입 후 setup.sh 실행 시간 < 3분 (Fast-Track 휠 복원 < 5초), 소스 컴파일 Fallback 0건

**Constraints**: `FORCE_CMAKE=1`, `CFLAGS="-march=x86-64"`, `-DCMAKE_CUDA_ARCHITECTURES=61`, `-DGGML_NATIVE=OFF`

**Scale/Scope**: `scripts/make_seed_pack.sh`, `tests/unit/test_seed_pack_legacy.py`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙 - make_seed_pack.sh CMAKE 인자 테스트 작성)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙 - DoD-001 ~ DoD-003 준수)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙)

## Project Structure

### Documentation (this feature)

```text
specs/031-fix-seed-pack-cuda-arch/
├── spec.md              # Feature specification
├── plan.md              # Implementation Plan (/speckit-plan output)
├── research.md          # Phase 0 output (/speckit-plan output)
├── data-model.md        # Phase 1 output (/speckit-plan output)
├── quickstart.md        # Phase 1 output (/speckit-plan output)
├── contracts/           # Phase 1 CLI Contract output
│   └── seed-pack-cuda-contract.md
└── tasks.md             # Phase 2 output (/speckit-tasks output - pending)
```

### Source Code (repository root)

```text
scripts/
└── make_seed_pack.sh    # FR-001: i7-930 휠 사전 컴파일 구문에 FORCE_CMAKE=1, -DCMAKE_CUDA_ARCHITECTURES=61 및 -DGGML_NATIVE=OFF 추가

wheels/
└── legacy_i7_930/       # GTX 1070 sm_61 타겟 코드 포함 휠 바이너리 보관함

tests/
└── unit/
    └── test_seed_pack_legacy.py  # FR-003: make_seed_pack.sh CMAKE_CUDA_ARCHITECTURES 인자 수록 정적/동적 검증 테스트
```

**Structure Decision**: Single project layout with shell scripts under `scripts/`, prebuilt legacy wheels in `wheels/legacy_i7_930/`, and pytest test cases under `tests/unit/`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*violations: None. Configuration option update and unit test extension.*
