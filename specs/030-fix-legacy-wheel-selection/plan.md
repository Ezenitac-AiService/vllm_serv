# Implementation Plan: 구형 i7-930 타겟 패키지 설치 시 llama_cpp_python 사전 빌드 휠 정확한 선택 및 복원 오류 수정 (030-fix-legacy-wheel-selection)

**Branch**: `030-fix-legacy-wheel-selection` | **Date**: 2026-07-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/030-fix-legacy-wheel-selection/spec.md`

## Summary

`scripts/setup.sh` 파이프라인에서 `legacy-i7-930-gtx1070` 타겟 프로필 감지 시 사전 빌드 휠 탐색 구문을 개정합니다. 기존 `ls wheels/legacy_i7_930/*.whl | head -n 1` 알파벳 정렬에 의한 타 패키지(`annotated_doc`) 잘못된 선택 문제를 해결하기 위해 `ls -v wheels/legacy_i7_930/llama_cpp_python*.whl 2>/dev/null | tail -n 1` 패턴으로 `llama_cpp_python` 휠을 명시적으로 탐색 및 선택합니다.

복원 시 `--no-index --find-links wheels/legacy_i7_930` 옵션을 사용하여 로컬 오프라인 의존성 휠 패키지 고속 설치를 보장하며, 휠 유실 또는 휠 복원 후 GPU 오프로드 검증(`llama_supports_gpu_offload()`) 실패 시 에러 종료 없이 경고 출력 후 소스 컴파일 파이프라인으로 안전하게 자동 Fallback 하도록 구현합니다.

## Technical Context

**Language/Version**: Python 3.12+, Bash Shell Scripting (`set -eo pipefail`)

**Primary Dependencies**: `uv`, `llama-cpp-python` (with CUDA GGML backend)

**Storage**: Local files (`wheels/legacy_i7_930/`, `dist/vllm_serv_seed.tar.gz`)

**Testing**: `pytest`, Bash script execution tests (`tests/unit/test_seed_pack_legacy.py`)

**Target Platform**: Linux (Ubuntu 24.04 LTS), Platform C (`legacy-i7-930-gtx1070`)

**Project Type**: Server Deployment Pipeline & Seed Pack CLI Tool

**Performance Goals**: Fast-Track 휠 복원 설치 시간 < 5초, i7-930 머신 전체 구축 시간 < 3분

**Constraints**: 로컬 오프라인 패키지 설치 (`--no-index --find-links wheels/legacy_i7_930`), 휠 매칭 정밀화 (`ls -v wheels/legacy_i7_930/llama_cpp_python*.whl | tail -n 1`), 검증 실패 시 자동 소스 컴파일 Fallback

**Scale/Scope**: `scripts/setup.sh`, `wheels/legacy_i7_930/`, `tests/unit/test_seed_pack_legacy.py`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙 - shell script 및 fast-track 테스트 작성)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙 - DoD-001 ~ DoD-004 준수)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙)

## Project Structure

### Documentation (this feature)

```text
specs/030-fix-legacy-wheel-selection/
├── spec.md              # Feature specification
├── plan.md              # Implementation Plan (/speckit-plan output)
├── research.md          # Phase 0 output (/speckit-plan output)
├── data-model.md        # Phase 1 output (/speckit-plan output)
├── quickstart.md        # Phase 1 output (/speckit-plan output)
├── contracts/           # Phase 1 CLI/Script Contract output
│   └── wheel-installation-contract.md
└── tasks.md             # Phase 2 output (/speckit-tasks output - pending)
```

### Source Code (repository root)

```text
scripts/
└── setup.sh             # FR-001..FR-004: i7-930 llama_cpp_python 휠 명시적 매칭, 오프라인 설치 및 Fallback 개정

wheels/
└── legacy_i7_930/       # i7-930 전용 사전 컴파일 .whl 및 의존성 휠 저장소

tests/
└── unit/
    └── test_seed_pack_legacy.py  # 휠 명시적 탐색 및 오프라인 주입/Fallback 검증 테스트 케이스 추가
```

**Structure Decision**: Single project layout with shell scripts under `scripts/`, prebuilt legacy wheels in `wheels/legacy_i7_930/`, and pytest test cases under `tests/unit/`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*violations: None. Shell pipeline logic update and test extension.*
