# Implementation Plan: Tier 4 uv 휠 캐시 실측 검증 및 불일치 시 조건부 --no-cache-dir C++ 소스 재컴파일 파이프라인 (057-fix-uv-no-cache-source-compilation)

**Branch**: `057-fix-uv-no-cache-source-compilation` | **Date**: 2026-07-31 | **Spec**: [`spec.md`](file:///home/dev/storage/vllm_serv/specs/057-fix-uv-no-cache-source-compilation/spec.md)

**Input**: Feature specification from `/home/dev/storage/vllm_serv/specs/057-fix-uv-no-cache-source-compilation/spec.md`

---

## Summary

서비스 타깃 서버 이관 3차 실측 로그 분석 결과, Tier 4 파이프라인 진입 시 `uv` 패키지 매니저가 `~/.cache/uv/wheels` 디렉터리의 이전 CPU 전용 `llama-cpp-python` 휠을 감지하고 5ms 만에 재설치하여 C++ 소스 컴파일 및 동적 `CMAKE_ARGS`를 무력화시키는 결함이 규명되었습니다.

본 계획서는 이를 해결하기 위하여 **Option A (2단계 조건부 uv 휠 캐시 검증 파이프라인)**을 구축합니다. `setup.sh` Tier 4 진입 시 먼저 가상환경 휠의 `llama_supports_gpu_offload()` 3중 가속 검증을 실행하여 성공 시 수 초 만에 기존 휠을 재사용하고, 검증 실패(CPU 전용 휠) 시에만 `uv pip uninstall` 후 `CMAKE_ARGS="$DETECTED_CMAKE_ARGS" uv pip install --no-cache-dir "llama-cpp-python[server]" --no-binary llama-cpp-python` 구문으로 캐시를 무효화하고 실제 C++ 소스코드를 타깃 머신 하드웨어 사양에 맞게 컴파일합니다. 또한 `make_seed_pack.sh` 사전 휠 재사용/Post-Build 3중 검증 및 `unpack_seed.sh` 프로젝트 루트(`vllm_serv/`) 안전 보존 압축 해제 파이프라인을 완성합니다.

---

## Technical Context

**Language/Version**: Python 3.10+, Bash shell script  
**Primary Dependencies**: `uv` (0.3+), `llama-cpp-python`, `nvidia-smi`, `gcc`/`g++`, `nvcc` (CUDA Toolkit 12.x)  
**Storage**: Local files (`vllm_serv_seed.tar.gz`, `wheels/legacy_i7_930/*.whl`, `config/platform_profiles.json`)  
**Testing**: `pytest` (`uv run pytest`), bash syntax check (`bash -n`), `verify_wheel_binary.py`  
**Target Platform**: Linux server (x86_64, Ubuntu 22.04 LTS), Nehalem i7 930 + GTX 1070, Haswell Xeon + GTX 1080 Ti, RTX 3060  
**Project Type**: Python CLI & Background LLM Inference Service Framework  
**Performance Goals**: 레거시 서비스 이관 마이그레이션 0.05초 Fast-Track 복원; 결함 휠 존재 시 자동 무효화 후 100% C++ 소스 재컴파일  
**Constraints**: 헌법 v1.6.0 준수, Real-Integration TDD, 가상환경 격리 (`uv run`), 한국어 소통  
**Scale/Scope**: `scripts/setup.sh`, `scripts/make_seed_pack.sh`, `scripts/unpack_seed.sh`, `src/core/cpu_detector.py`, `tests/unit/test_seed_pack.py`

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙)
- [x] 목업은 유료/제한 API로 엄격히 제한하고 실물 시스템/소켓/OS 인자 및 실제 호출 플래그(REAL_API_CALL=1) 기반 실측 검증 계획이 포함되어 있는가? (실체적 테스트 및 수렴 검증 원칙)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙)
- [x] 비파괴적 문서 수정 원칙을 준수하는가? (비파괴적 문서 수정 원칙)
- [x] uv 패키지 매니저 및 가상환경 격리 표준(uv run)을 준수하는가? (uv 패키지 및 환경 관리 원칙)
- [x] 전체 회귀 테스트 수트 및 Playwright 기반 E2E 브라우저 실측 검증 계획이 포함되어 있는가? (의무적 회귀 테스트 및 브라우저 E2E 검증 원칙)

---

## Project Structure

### Documentation (this feature)

```text
specs/057-fix-uv-no-cache-source-compilation/
├── plan.md              # Implementation plan (this file)
├── research.md          # Phase 0 Research findings
├── data-model.md        # Phase 1 Data Model & Entity definitions
├── quickstart.md        # Phase 1 Quickstart Validation Guide
├── contracts/           # Phase 1 Interface contracts
│   └── fallback-pipeline-api.json
└── tasks.md             # Phase 2 Actionable Tasks (/speckit-tasks output)
```

### Source Code Structure (repository root)

```text
/home/dev/storage/vllm_serv/
├── unpack_seed.sh -> scripts/unpack_seed.sh  # Project root shortcut
├── scripts/
│   ├── setup.sh                               # Tier 4 2-stage conditional uv cache validation
│   ├── make_seed_pack.sh                      # Prebuilt wheel reuse & post-build 3-way check
│   ├── unpack_seed.sh                        # Safe extraction helper script (-k -p)
│   └── verify_wheel_binary.py                 # Live verification script (AVX, CUDA)
├── src/
│   └── core/
│       └── cpu_detector.py                    # GPU compute capability & SIMD detector + fallback
├── config/
│   └── platform_profiles.json                # Platform profiles for dev, pascal, legacy
└── tests/
    └── unit/
        └── test_seed_pack.py                  # Unit tests for seed pack, unpack, & cache invalidation
```

**Structure Decision**: Single repository layout with bash scripts in `scripts/`, core detector in `src/core/`, platform profiles in `config/`, and unit tests in `tests/unit/`.

---

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | None | All constitution principles satisfied without violations |
