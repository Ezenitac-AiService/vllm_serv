# Implementation Plan: make_seed_pack.sh 레거시 사전 휠 Post-Build AVX 실측 검증 로직 및 빌드 플래그 정밀화 (059-fix-legacy-wheel-avx-build)

**Branch**: `059-fix-legacy-wheel-avx-build` | **Date**: 2026-07-31 | **Spec**: [`spec.md`](file:///home/dev/storage/vllm_serv/specs/059-fix-legacy-wheel-avx-build/spec.md)

**Input**: Feature specification from `/specs/059-fix-legacy-wheel-avx-build/spec.md`

---

## Summary

`make_seed_pack.sh` 실행 시 레거시 사전 휠(`wheels/legacy_i7_930/*.whl`) 빌드 과정 후 Post-Build 실측 검증 시, `verify_wheel_binary.py` 바이너리 바이트 스캐너가 `libggml-cuda.so` 내 CUDA GPU 디바이스 데이터 바이트를 CPU AVX 바이트로 오판단하여 `❌ [POST-BUILD FAIL]` 오류를 발생시키고 결함 휠로 오인하여 무단 삭제하는 결함을 원천 규명하고 해결합니다.

본 계획서는 `verify_wheel_binary.py` 스캐너가 CUDA 디바이스 전용 공유 라이브러리와 CPU 호스트 공유 라이브러리를 명확히 구분하여 검증하도록 바이트 스캔 대상을 정밀화하고, `make_seed_pack.sh` 휠 컴파일 시 `scikit-build-core` 공식 규격 환경 변수인 `SKBUILD_CMAKE_ARGS`를 함께 명시하여 이중 방어망을 구축합니다.

---

## Technical Context

**Language/Version**: Python 3.10+, Bash shell script  
**Primary Dependencies**: `uv` (0.3+), `scikit-build-core`, `cmake`, `llama-cpp-python`  
**Storage**: Local files (`wheels/legacy_i7_930/*.whl`, `scripts/make_seed_pack.sh`, `scripts/verify_wheel_binary.py`)  
**Testing**: `pytest` (`uv run pytest tests/unit/test_seed_pack.py`), `verify_wheel_binary.py`  
**Target Platform**: Linux x86_64, Nehalem i7 930 + GTX 1070, Haswell Xeon + GTX 1080 Ti  
**Project Type**: Python CLI & Background LLM Inference Service Framework  
**Performance Goals**: `make_seed_pack.sh` 사전 휠 빌드 및 Post-Build 검증 성공률 100%, False Positive 0건  
**Constraints**: 헌법 v1.6.0 준수, Real-Integration TDD, 가상환경 격리 (`uv run`), 한국어 소통  
**Scale/Scope**: `scripts/verify_wheel_binary.py`, `scripts/make_seed_pack.sh`, `tests/unit/test_seed_pack.py`

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
specs/059-fix-legacy-wheel-avx-build/
├── plan.md              # Implementation plan (this file)
├── research.md          # Phase 0 Research findings
├── data-model.md        # Phase 1 Data Model & Entity definitions
├── quickstart.md        # Phase 1 Quickstart Validation Guide
├── contracts/           # Phase 1 Interface contracts
│   └── wheel-verification-contract.json
└── tasks.md             # Phase 2 Actionable Tasks (/speckit-tasks output)
```

### Source Code Structure (repository root)

```text
/home/dev/storage/vllm_serv/
├── scripts/
│   ├── make_seed_pack.sh                      # Prebuilt wheel build pipeline (SKBUILD_CMAKE_ARGS added)
│   └── verify_wheel_binary.py                 # Post-Build 3-way check script (CUDA vs CPU .so target scanning)
└── tests/
    └── unit/
        └── test_seed_pack.py                  # Unit tests for wheel verification & seed pack pipeline
```

---

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | None | All constitution principles satisfied without violations |
