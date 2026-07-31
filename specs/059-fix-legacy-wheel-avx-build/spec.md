# Feature Specification: make_seed_pack.sh 레거시 사전 휠 Post-Build AVX 실측 검증 로직 및 빌드 플래그 정밀화 (059-fix-legacy-wheel-avx-build)

**Feature Branch**: `059-fix-legacy-wheel-avx-build`  
**Created**: 2026-07-31  
**Status**: Draft  
**Input**: User error log & report: `make_seed_pack.sh` 사전 휠 빌드 후 Post-Build 실측 검증 단계에서 `verify_wheel_binary.py` 바이너리 바이트 스캐너가 `libggml-cuda.so` 내 CUDA GPU 바이너리 데이터 패턴을 AVX 명령어로 감지하여 `❌ [POST-BUILD FAIL]` 오류를 내고 결함 휠로 오판단하여 삭제하는 현상 분석 및 리서치 요청.

---

## Overview & Background

`make_seed_pack.sh` 실행 시 레거시 서비스 타깃(`legacy-i7-930-gtx1070`, Nehalem CPU, GTX 1070)용 사전 컴파일 휠(`wheels/legacy_i7_930/*.whl`)을 컴파일한 후, Post-Build 3중 실측 검증 도구인 `scripts/verify_wheel_binary.py`를 호출하여 AVX 무결성 및 CUDA 가속 활성 상태를 검증합니다.

그러나 현행 `verify_wheel_binary.py`의 `scan_so_with_python_bytes()` 바이트 스캐너는 `.whl` 패키지 내 모든 `.so` 파일(CUDA GPU 커널 바이너리인 `libggml-cuda.so` 포함)에 대해 전체 바이너리 바이트 스캔을 수행합니다. CUDA SASS/PTX 디바이스 코드 및 내장 가속 데이터 테이블에 존재하는 `0xC4`/`0xC5` 바이트 패턴이 AVX VEX 오코드 예비 패턴으로 오감지(False Positive)되어 총 3,109,407건의 AVX 오검출 결과를 산출하고, 휠을 삭제하는 결함이 발견되었습니다.

본 명세는 `verify_wheel_binary.py`의 바이너리 검증 대상 범위를 호스트 CPU 실행 파일(`ggml-cpu.so`, `libllama.so` 등)로 정밀하게 한정하고, `make_seed_pack.sh` 빌드 환경 변수에 `scikit-build-core` 표준 규격인 `SKBUILD_CMAKE_ARGS`를 보강하여 개발 머신에서 빌드하더라도 레거시 타깃 사전 휠 검증을 100% 정상 수행할 수 있도록 개선합니다.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - verify_wheel_binary.py 바이너리 스캐너 정밀화 및 False Positive 100% 제거 (Priority: P1) 🎯 MVP

개발 머신 또는 CI 파이프라인에서 `./scripts/make_seed_pack.sh`를 실행할 때, `verify_wheel_binary.py`가 CUDA GPU 바이너리(`libggml-cuda.so`) 내 데이터 패턴을 AVX 바이트로 오판단하지 않고 CPU 호스트 바운드 라이브러리(`ggml-cpu`, `libllama` 등)의 AVX 무결성을 정밀 검증하여 `✓ [POST-BUILD SUCCESS]` 결과를 리턴합니다.

**Why this priority**: 사전 휠 빌드가 성공하더라도 오검출 검증기로 인해 유효한 사전 휠 아티팩트가 자동 삭제되는 문제를 차단해야 안정적인 멀티 플랫폼 배포 아카이브가 구성됩니다.

**Independent Test**: `uv run python scripts/verify_wheel_binary.py wheels/legacy_i7_930/llama_cpp_python-*.whl` 실행 시 CUDA 디바이스 라이브러리와 CPU 호스트 라이브러리를 구분 검증하여 100% `✓ Wheel verified valid` 결과와 Exit Code 0을 리턴합니다.

**Acceptance Scenarios**:

1. **Given** `make_seed_pack.sh` 사전 휠 컴파일 완료 후, **When** `verify_wheel_binary.py` 검증 단계에 진입하면, **Then** CUDA 디바이스 전용 공유 라이브러리(`ggml-cuda`) 내 디바이스 데이터 바이트는 CPU AVX 검사 대상에서 상호 분리되어 오검출이 발생하지 않아야 한다.
2. **Given** Nehalem i7-930 타깃용 사전 휠일 때, **Then** CPU 호스트 라이브러리(`ggml-cpu.so`, `libllama.so`)에 대해서만 AVX 명령어 무결성을 엄격 검증(AVX=0)하고 검증 성공 시 휠을 아카이브에 수록해야 한다.

---

### User Story 2 - scikit-build-core 표준 환경 변수(SKBUILD_CMAKE_ARGS) 보강 및 빌드 정밀화 (Priority: P2)

`make_seed_pack.sh` 및 사전 빌드 파이프라인에서 `scikit-build-core` 백엔드가 인지하는 공식 환경 변수 `SKBUILD_CMAKE_ARGS`와 `CMAKE_ARGS`, `CFLAGS`, `CXXFLAGS`를 동시에 정밀 전달하여 어떠한 컴파일러 환경에서도 `-DGGML_AVX=OFF` 플래그가 전파되도록 합니다.

**Why this priority**: PEP 517/518 격리 빌드 시스템 환경에서 빌드 백엔드 패키저가 CMake 인자를 100% 신뢰성 있게 전달받도록 보장합니다.

**Independent Test**: `make_seed_pack.sh --build-legacy` 실행 시 생성된 휠의 CPU 공유 라이브러리가 타깃 CPU 하드웨어 제약(AVX=OFF)을 엄격히 준수합니다.

**Acceptance Scenarios**:

1. **Given** `make_seed_pack.sh` 사전 휠 빌드 수행 시, **When** `uv run pip wheel`이 실행되면, **Then** `SKBUILD_CMAKE_ARGS` 및 `CMAKE_ARGS`가 명시되어 `scikit-build-core`에 CMake 플래그가 정밀 전달되어야 한다.

---

### Edge Cases

- `verify_wheel_binary.py`에 `--allow-avx` 옵션이 전달된 경우 host CPU의 AVX 지원 유무를 참조하여 허용 수준을 동적으로 조정한다.
- CUDA 가속이 비활성화된 CPU 전용 빌드 휠의 경우 `cuda_enabled=False` 상태를 정상 감지하고 명시적 안내 메시지를 출력한다.

---

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `./scripts/make_seed_pack.sh` 실행 시 `Post-Build 3중 실측 검증` 단계가 `❌ [POST-BUILD FAIL]` 오검출 없이 100% `✓ [POST-BUILD SUCCESS]`로 통과한다.
- **DoD-002**: `verify_wheel_binary.py` 검증 도구가 CUDA GPU 바이너리와 CPU 호스트 라이브러리를 명확히 구분 스캔한다.
- **DoD-003**: `tests/unit/test_seed_pack.py` 회귀 테스트 수트가 100% 통과한다.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `scripts/verify_wheel_binary.py`의 `verify_wheel` 및 바이너리 검사 함수는 `.so` 파일의 주 용도(CUDA GPU 디바이스 커널 라이브러리 vs CPU 호스트 공유 라이브러리)를 정밀 구분하여, CPU 호스트 라이브러리에 집중하여 AVX 무결성을 평가해야 한다.
- **FR-002**: `scripts/make_seed_pack.sh`의 휠 컴파일 구문에서 `SKBUILD_CMAKE_ARGS`와 `CMAKE_ARGS`, `CFLAGS`, `CXXFLAGS`를 함께 설정하여 `scikit-build-core` 환경에서 CMake 빌드 옵션이 누락 없이 전달되도록 조율해야 한다.
- **FR-003**: `tests/unit/test_seed_pack.py`에 `verify_wheel_binary.py` 분리 스캔 검증 및 `make_seed_pack.sh` Post-Build 성공 단정을 수록해야 한다.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `make_seed_pack.sh` 사전 휠 Post-Build 검증 성공률 100% (False Positive 0건).
- **SC-002**: `verify_wheel_binary.py`의 CPU host `.so` 라이브러리 정밀 검사 정확도 100%.
- **SC-003**: `uv run pytest` 수트 Pass율 100%.

---

## Assumptions

- `scikit-build-core` (0.9.x+) 백엔제는 `SKBUILD_CMAKE_ARGS` 및 `CMAKE_ARGS` 환경 변수를 CMake 인자로 해석한다.
- `libggml-cuda.so` 파일은 NVIDIA CUDA GPU 연산 커널을 포함하며 호스트 CPU의 AVX 직접 명령어와 무관하게 NVPTX/SASS 바이너리로 동작한다.
