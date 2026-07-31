# Implementation Plan: 플랫폼 프로필 매칭 정교화 및 출력 메시지 다듬기

**Branch**: `022-refine-platform-profile-matching` | **Date**: 2026-07-30 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/022-refine-platform-profile-matching/spec.md)

**Input**: Feature specification from `/specs/022-refine-platform-profile-matching/spec.md`

## Summary

`src/core/cpu_detector.py`에서 생성하는 CMake 컴파일 인자 문자열의 공백 누락 버그(`-DGGML_F16C=ON-DGGML_FMA=ON`)를 수정하고, `config/platform_profiles.json` 및 `match_platform_profile()`을 개선하여 Xeon E3-1231 v3(Haswell, AVX2 지원) + GTX 1080 Ti(Pascal, sm_61)와 같은 조합을 기존 Nehalem(AVX 미지원) 레거시 프로필로 오인하지 않도록 CPU SIMD 지원과 GPU Compute Capability를 종합 판별한다. 또한 `make_seed_pack.sh`, `status_server.sh`, `setup.sh`의 예시 및 마이그레이션 안내 문구를 다듬는다.

## Technical Context

**Language/Version**: Python 3.12, Bash
**Primary Dependencies**: Pydantic v2, pytest, argparse, shutil, subprocess
**Storage**: File-based JSON (`config/platform_profiles.json`)
**Testing**: `pytest` (`tests/unit/test_cpu_detector.py`, `tests/unit/test_shell_scripts.py`)
**Target Platform**: Linux x86_64 (NVIDIA GPU CUDA Acceleration)
**Project Type**: CLI / Operational Infrastructure / LLM Serving Engine
**Performance Goals**: 하드웨어 감지 및 프로필 매칭 리포트 1초 미만 (`< 1.0s`)
**Constraints**: 100% 하위 호환성 유지, 외부 서드파티 무거운 라이브러리 추가 금지, pytest 테스트 100% 통과
**Scale/Scope**: 5개 스크립트/모듈 파일 (`cpu_detector.py`, `platform_profiles.json`, `status_server.sh`, `setup.sh`, `make_seed_pack.sh`)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)

## Project Structure

### Documentation (this feature)

```text
specs/022-refine-platform-profile-matching/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── cli_contracts.md # CLI 계약 명세
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code (repository root)

```text
src/
└── core/
    ├── cpu_detector.py        # CMake 인자 공백 서식 수정 및 AVX2+GPU 조합 프로필 매칭 로직
    └── config_manager.py      # 플랫폼 프로필 로더

config/
└── platform_profiles.json     # Haswell + Pascal 프로필 (pascal-avx2-gtx1080ti) 추가

scripts/
├── status_server.sh           # 리포트 문구 다듬기
├── setup.sh                   # 프로필 표시 및 CMAKE_ARGS 전파
└── make_seed_pack.sh          # 이관 안내문 다듬기

tests/
└── unit/
    ├── test_cpu_detector.py   # CMake 인자 공백 및 프로필 매칭 유닛 테스트
    └── test_shell_scripts.py # 쉘 스크립트 실행 및 안내 문구 유닛 테스트
```

**Structure Decision**: 기존 `src/core/cpu_detector.py` 단일 모듈 및 `scripts/` 쉘 스크립트 구조를 유지하며, `config/platform_profiles.json` 프로필 항목을 확장한다.

## Complexity Tracking

> Violation: 없음 (모든 프로젝트 헌법 원칙 준수)
