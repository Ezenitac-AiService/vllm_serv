# Feature Specification: i7-930/GTX 1070 타겟 시드 팩 사전 빌드 휠 CMAKE_CUDA_ARCHITECTURES 명시 및 고속 복원 검증 통과 (031-fix-seed-pack-cuda-arch)

**Feature Branch**: `031-fix-seed-pack-cuda-arch`

**Created**: 2026-07-30

**Status**: Draft

**Input**: User log analysis (`log.txt`): i7-930 머신(GTX 1070)에서 시드 팩 복원 후 `setup.sh` 실행 시 `llama_cpp_python` 휠이 로드되었으나 CUDA 아키텍처 설정(`-DCMAKE_CUDA_ARCHITECTURES=61`) 누락으로 인해 `llama_supports_gpu_offload()` 검증에 실패하고 소스 컴파일 파이프라인으로 Fallback되는 이슈 해결.

## Clarifications

### Session 2026-07-30

- Q: i7-930 휠 사전 컴파일 시 CMAKE 및 빌드 환경 변수 보강 플래그 구성 → A: Option A (`FORCE_CMAKE=1`, `CFLAGS="-march=x86-64"`, `CMAKE_ARGS="-DGGML_CUDA=ON -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_F16C=OFF -DGGML_FMA=OFF -DGGML_NATIVE=OFF -DCMAKE_CUDA_ARCHITECTURES=61"` 플래그를 모두 명시하여 호스트 CPU 명령어 누출 방지 및 GTX 1070 전용 휠 생성)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - i7-930 및 GTX 1070 전용 CUDA 아키텍처 사전 빌드 휠 생성 및 100% Fast-Track 복원 통과 (Priority: P1) 🎯 MVP

시스템 엔지니어가 `scripts/make_seed_pack.sh`를 실행할 때, `legacy-i7-930` 전용 사전 빌드 휠이 GTX 1070 GPU Compute Capability 6.1에 맞춰 `-DCMAKE_CUDA_ARCHITECTURES=61`, `-DGGML_NATIVE=OFF`, `FORCE_CMAKE=1` 플래그로 컴파일되어 시드 팩에 번들링되며, 타겟 i7-930 머신에서 `scripts/setup.sh` 구동 시 소스 컴파일 Fallback 없이 `llama_supports_gpu_offload()` GPU 가속 검증을 100% 한 번에 통과합니다.

**Why this priority**: 사전 빌드 휠이 로드되었음에도 CUDA 아키텍처 플래그 누락으로 GPU 검증이 실패하여 소스 컴파일(15~30분 소요)로 되돌아가는 현상을 완전 방지하고 3분 이내 구축 목표를 실현하기 위함입니다.

**Independent Test**: `make_seed_pack.sh` 실행 후 생성된 `wheels/legacy_i7_930/llama_cpp_python*.whl`을 i7-930/GTX 1070 모의 환경에서 `setup.sh`로 주입 시 소스 컴파일 파이프라인으로 Fallback되지 않고 Fast-Track 휠 복원 및 GPU 가속 검증이 통과하는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** `scripts/make_seed_pack.sh` 스크립트 구동 시, **When** i7-930 휠 사전 컴파일 구문이 실행되면, **Then** `FORCE_CMAKE=1` 환경변수와 `CMAKE_ARGS`에 `-DCMAKE_CUDA_ARCHITECTURES=61` 및 `-DGGML_NATIVE=OFF` 플래그가 명시적으로 전달되어 GTX 1070 전용 휠 바이너리가 생성되어야 한다.
2. **Given** GTX 1070 GPU 환경의 i7-930 머신에서 `scripts/setup.sh`를 구동할 때, **When** 사전 빌드된 `llama_cpp_python` 휠을 Fast-Track 복원하면, **Then** `[SETUP WARN] ⚠️ 사전 빌드 휠 복원 후 GPU 가속 검증 실패` 경고 로그가 발생하지 않고 `✓ i7-930 사전 빌드 휠 Fast-Track 설치 및 CUDA GPU 가속 활성화 확인 완료` 성공 로그와 함께 파이프라인이 즉시 완료되어야 한다.

---

### User Story 2 - 시드 팩 빌드 스크립트 CMAKE 인자 검증 단위 테스트 추가 (Priority: P2)

개발자 및 유지보수자가 pytest 수트를 실행할 때, `make_seed_pack.sh` 스크립트 내 i7-930 사전 컴파일 인자에 `-DCMAKE_CUDA_ARCHITECTURES=61`, `-DGGML_NATIVE=OFF`, `FORCE_CMAKE=1`이 올바르게 포함되어 있는지 자동 검증합니다.

**Why this priority**: 향후 시드 팩 스크립트 수정 시 CUDA 아키텍처 및 NATIVE 옵션 누락으로 인한 리그레션을 예방하기 위함입니다.

**Independent Test**: `tests/unit/test_seed_pack_legacy.py` 실행 시 `make_seed_pack.sh` 내 `CMAKE_CUDA_ARCHITECTURES=61` 및 `GGML_NATIVE=OFF` 인자 포함 여부를 검증하는 테스트가 통과하는지 확인합니다.

**Acceptance Scenarios**:

1. **Given** `tests/unit/test_seed_pack_legacy.py` 단위 테스트 수트를 구동하면, **When** `make_seed_pack.sh` 구문 검사를 수행하면, **Then** `-DCMAKE_CUDA_ARCHITECTURES=61` 및 `-DGGML_NATIVE=OFF` 인자가 선언되어 있음을 성공적으로 검증해야 한다.

---

### Edge Cases

- 시드 팩을 생성하는 호스트 장비(Platform A/B)의 CUDA Toolkit 버전과 타겟 머신의 CUDA 드라이버 버전 간 호환성 범위 내에서 sm_61 아티팩트가 정상 작동하는가?
- `make_seed_pack.sh`에서 `pip wheel` 빌드 시 PEP 517 분리 빌드 환경에 `CMAKE_ARGS` 및 `FORCE_CMAKE=1` 환경 변수가 정상 전입되는가?

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `scripts/make_seed_pack.sh` 스크립트의 i7-930 휠 사전 컴파일 구문에 `FORCE_CMAKE=1` 및 `CMAKE_ARGS="-DGGML_CUDA=ON -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_F16C=OFF -DGGML_FMA=OFF -DGGML_NATIVE=OFF -DCMAKE_CUDA_ARCHITECTURES=61"` 명시 지정 완료
- **DoD-002**: `make_seed_pack.sh`로 빌드된 사전 휠 주입 시 `setup.sh`에서 Fallback 경고 없이 `llama_supports_gpu_offload()` GPU 가속 검증 100% 통과 확인
- **DoD-003**: `tests/unit/test_seed_pack_legacy.py`에 CMAKE_CUDA_ARCHITECTURES 및 GGML_NATIVE=OFF 인자 수록 검증 테스트 추가 및 100% 통과

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (i7-930 휠 사전 컴파일 시 CMAKE_CUDA_ARCHITECTURES=61 및 GGML_NATIVE=OFF 명시)**: `scripts/make_seed_pack.sh` 실행 시 `legacy-i7-930` 전용 휠 컴파일 구문에서 `FORCE_CMAKE=1` 환경변수를 전달하고 `CMAKE_ARGS`에 `-DCMAKE_CUDA_ARCHITECTURES=61` 및 `-DGGML_NATIVE=OFF`를 명시적으로 추가하여 호스트 CPU 명령어 누출 없는 GTX 1070 사전 빌드 휠을 생성해야 한다.
- **FR-002 (사전 빌드 휠 GPU 가속 검증 100% 통과 보장)**: `scripts/setup.sh` 파이프라인에서 i7-930 타겟 감지 시 복원된 사전 빌드 휠이 `llama_supports_gpu_offload()` 검증을 100% 통과하여 소스 컴파일 파이프라인으로 Fallback 되지 않고 Fast-Track 복원을 완성해야 한다.
- **FR-003 (시드 팩 CMAKE 인자 회귀 검증 테스트 수록)**: `tests/unit/test_seed_pack_legacy.py`에 `make_seed_pack.sh` 내 i7-930 휠 생성 인자의 `-DCMAKE_CUDA_ARCHITECTURES=61`, `-DGGML_NATIVE=OFF` 수록 여부를 정적/동적으로 검증하는 테스트 함수를 추가해야 한다.

### Key Entities

- **LegacyPrebuiltWheelArtifact**: `-DCMAKE_CUDA_ARCHITECTURES=61`, `-DGGML_NATIVE=OFF` 및 `-DGGML_CUDA=ON -DGGML_AVX=OFF` 인자로 사전 컴파일된 `llama-cpp-python` 파이썬 휠 바이너리.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `make_seed_pack.sh`로 생성된 시드 팩 휠 주입 후 `setup.sh` 실행 시 소스 컴파일 Fallback 경고 0건 및 100% Fast-Track 검증 통과
- **SC-002**: `tests/unit/test_seed_pack_legacy.py` 및 전체 pytest 수트 100% 통과

## Assumptions

- GTX 1070 GPU의 Compute Capability는 `6.1`이며, CMake의 `CMAKE_CUDA_ARCHITECTURES` 값으로 `61`을 지정함.
- `make_seed_pack.sh` 실행 환경의 nvcc 코어 컴파일러는 `sm_61` 타겟 코드 조립을 지원함.
