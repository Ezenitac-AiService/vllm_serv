# Implementation Plan: 구형 i7-930 플랫폼 전용 사전 컴파일 라이브러리 시드 팩(Seed Pack) 번들링 및 고속 구축 (029-prebuild-legacy-seed-pack)

**Branch**: `029-prebuild-legacy-seed-pack` | **Date**: 2026-07-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/029-prebuild-legacy-seed-pack/spec.md`

## Summary

`scripts/make_seed_pack.sh` 스크립트를 확장하여 구형 Nehalem CPU(i7-930)에 최적화된 사전 컴파일 휠(`.whl`) 아티팩트를 명시적 컴파일 인자(`CMAKE_ARGS="-DGGML_CUDA=ON -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_F16C=OFF -DGGML_FMA=OFF"` 및 `CFLAGS="-march=x86-64"`)로 생성 후 시드 팩 아카이브(`dist/vllm_serv_seed.tar.gz`)에 번들링합니다.

`scripts/setup.sh` 파이프라인에서는 `legacy-i7-930-gtx1070` 하드웨어 프로필 감지 시 C++ 소스 재컴파일(15~30분 소요)을 건너뛰고 번들링된 사전 빌드 휠을 `uv pip install`로 3초 내 고속 주입하여 구축 시간을 **3분 이내로 단축**합니다. 사전 빌드 휠이 유실된 경우 소스 컴파일 파이프라인으로 안전하게 Fallback하며, 현대적 AVX2 장비(Platform A/B)는 플랫폼 전용 소스 컴파일 파이프라인을 그대로 유지합니다.

## Technical Context

**Language/Version**: Python 3.12+, Bash Shell Scripting (`set -eo pipefail`)

**Primary Dependencies**: `uv`, `llama-cpp-python` (with CUDA GGML backend)

**Storage**: Local files (`wheels/legacy_i7_930/`, `dist/vllm_serv_seed.tar.gz`)

**Testing**: `pytest`, Bash script syntax/execution tests (`tests/unit/test_shell_scripts.py`)

**Target Platform**: Linux (Ubuntu Server 24.04 LTS), Platform C (`legacy-i7-930-gtx1070`)

**Project Type**: Server Deployment Pipeline & Seed Pack CLI Tool

**Performance Goals**: i7-930 머신 구축 시간 기존 15~30분에서 3분 이내로 단축 (Fast-Track 휠 주입 <5초)

**Constraints**: i7-930 CPU 명령어 누출 방지 (`-march=x86-64`, `-DGGML_AVX=OFF`, `-DGGML_AVX2=OFF`), Platform A/B의 AVX2 가속 성능 보존

**Scale/Scope**: `scripts/make_seed_pack.sh`, `scripts/setup.sh`, `wheels/legacy_i7_930/`, 및 관련 단위 테스트

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙 - shell script 및 fast-track 테스트 작성)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙 - DoD-001 ~ DoD-004 준수)

## Project Structure

### Documentation (this feature)

```text
specs/029-prebuild-legacy-seed-pack/
├── spec.md              # Feature specification
├── plan.md              # Implementation Plan (/speckit-plan output)
├── research.md          # Phase 0 output (/speckit-plan output)
├── data-model.md        # Phase 1 output (/speckit-plan output)
├── quickstart.md        # Phase 1 output (/speckit-plan output)
├── contracts/           # Phase 1 CLI Contract output
│   └── seed-pack-cli-contract.md
└── tasks.md             # Phase 2 output (/speckit-tasks output - pending)
```

### Source Code (repository root)

```text
scripts/
├── make_seed_pack.sh    # FR-001: i7-930 사전 빌드 휠 컴파일 및 시드 팩 번들링
└── setup.sh             # FR-002..FR-005: Platform C 감지 시 uv pip install Fast-Track 주입 및 Fallback

wheels/
└── legacy_i7_930/       # i7-930 전용 사전 컴파일 .whl 저장소 (시드 팩 포함 대상)

tests/
└── unit/
    └── test_seed_pack_legacy.py  # FR-001..FR-005 시드 팩 및 Fast-Track 복원 검증 단위 테스트
```

**Structure Decision**: Single project layout with shell scripts under `scripts/`, prebuilt legacy wheels in `wheels/legacy_i7_930/`, and pytest test cases under `tests/unit/`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*violations: None. Pure configuration, shell pipeline and test extension.*
