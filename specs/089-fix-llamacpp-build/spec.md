# Feature Specification: llama.cpp 빌드 검증 및 휠 컴파일 파이프라인 수정 (Fix llama.cpp Build & Wheel Compilation Pipeline)

**Feature Branch**: `089-fix-llamacpp-build`

**Created**: 2026-08-04

**Status**: Draft

**Input**: User description: "llama.cpp 빌드에 문제가 있어 확인하고 스펙 작성 / 드라이버와 cudatoolkit cudnn 등의 업데이트도 확인해봐 / 드라이버와 툴킷등을 업데이트 하는 기능 추가 / 드라이버와 툴킷 라이브러리 버전 확인 후, 미달시 업데이트 하는 과정을 /home/bteam/vllm_serv/scripts/setup.sh 에 추가"

## Clarifications

### Session 2026-08-04
- Q: GPU 드라이버, CUDA Toolkit 및 cuDNN 버전 검증 및 업데이트 확인 방식 → A: Option A (자동 버전 검증 및 호환성 Fail-Fast 리포트: Driver, CUDA Toolkit, cuDNN 버전을 정밀 탐지하고 최소/권장 버전 기준 미달 시 상세 해결 가이드 출력 및 빌드 차단)
- Q: NVIDIA 드라이버 및 CUDA Toolkit 자동/원클릭 업데이트 제공 방식 → A: Option A (독립 헬퍼 스크립트 연동 `scripts/update_cuda_drivers.sh`: OS 패키지 매니저 기반 드라이버/CUDA Toolkit 자동 업데이트 스크립트를 작성하고 `setup.sh` 버전 미달 시 자동 연동)
- Q: `setup.sh` 내 드라이버/CUDA/cuDNN 버전 검증 및 자동 업데이트 동작 방식 → A: Option A (대화형 승인 후 인라인 자동 업데이트 & 비대화형 Fail-Fast 안내: TTY 대화형 환경에서는 사용자 승인 후 `setup.sh` 내에서 인라인 업데이트 실행, 비대화형 환경은 수동 명령 안내 후 중단)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - GPU 가속 기반 llama.cpp 휠 검증 및 자동 컴파일 (Priority: P1)

시스템 관리자 및 서비스 운영자가 서버 구축 스크립트(`setup.sh`) 실행 시 GPU 가속(CUDA)이 정상 활성화된 llama.cpp(llama-cpp-python) 패키지 및 NVIDIA 드라이버/CUDA Toolkit/cuDNN 버전을 자동으로 검증하고, 미지원 시 동적 C++ 소스 재컴파일을 수행하거나 업데이트 가이드를 제공하여 안정적인 GPU 서빙 환경을 보장한다.

**Why this priority**: CPU 전용 서빙은 추론 성능 저하를 유발하며, 호환되지 않는 드라이버/CUDA 버전은 C++ 컴파일 실패나 런타임 오류를 유발하므로 GPU 가속 및 드라이버/CUDA/cuDNN 버전에 대한 정밀 검증은 최우선 필수 항목이다.

**Independent Test**: CUDA 컴파일러(`nvcc`), NVIDIA 드라이버, cuDNN 버전을 `verify_wheel_binary.py` 및 `setup.sh`에서 정밀 탐지하여 호환 최소 버전(Driver >= 525, CUDA >= 12.0) 충족 여부를 검증하고, GPU 오프로드 가능 여부(`llama_supports_gpu_offload() == True`)를 확인한다.

**Acceptance Scenarios**:

1. **Given** CUDA Toolkit과 NVIDIA GPU가 사용 가능한 환경에서, **When** setup.sh 스크립트가 실행될 때, **Then** NVIDIA Driver, CUDA Toolkit, cuDNN 버전을 검증하고 최소 버전 충족 및 GPU 가속 지원이 확인되면 0.05초 이내에 빌드 단계를 스킵한다.
2. **Given** 호스트의 NVIDIA Driver 또는 CUDA Toolkit, cuDNN 버전이 최소 호환 기준에 미달할 때, **When** 대화형 TTY 환경에서 setup.sh가 실행되면, **Then** 사용자 프롬프트를 통해 승인받은 후 인라인 패키지 업데이트를 직접 실행하고 setup 파이프라인을 계속 진행한다.
3. **Given** 비대화형 CI/CD 환경에서 호스트 드라이버/CUDA/cuDNN 버전 미달이 감지될 때, **When** setup.sh가 실행되면, **Then** 빌드를 즉시 중단(Fail-Fast)하고 수동 패키지 업데이트 명령 가이드를 출력한다.
4. **Given** 가상환경 내 llama.cpp 패키지가 CPU 전용으로 설치되어 있거나 결함이 있는 상태에서, **When** 빌드 검증이 수행될 때, **Then** 캐시를 무효화하고 GPU CUDA 플래그(`-DGGML_CUDA=ON`)를 적용하여 동적 C++ 소스 재컴파일을 실행한다.

---

### User Story 2 - 하드웨어 SIMD 및 Compute Capability 동적 매칭 (Priority: P2)

다양한 하드웨어 플랫폼(Legacy CPU, 최신 GPU 등)에서 아키텍처 불일치(SIGILL 불법 명령 오류 등)를 방지하기 위해 호스트 CPU SIMD 세트 및 GPU Compute Capability를 자동 탐지하고 맞춤형 CMAKE 인자를 구성한다.

**Why this priority**: 레거시 CPU(예: AVX 미지원 CPU)나 특정 GPU 아키텍처에서 빌드된 바이너리 실행 시 런타임 크래시를 방지하기 위함이다.

**Independent Test**: `cpu_detector` 모듈을 실행하여 호스트 CPU(AVX/AVX2/FMA/F16C) 및 GPU Compute Capability(예: sm_86)를 감지하고, 올바른 CMAKE 인자 프로필이 반환되는지 확인한다.

**Acceptance Scenarios**:

1. **Given** 호스트 CPU의 SIMD 기능 및 GPU 아키텍처 정보가 주어졌을 때, **When** 하드웨어 탐지기가 가동되면, **Then** 감지된 속성에 알맞은 플랫폼 프로필(예: `dev-rtx3060`)과 동적 CMAKE 인자를 생성한다.

---

### User Story 3 - 4단계 휠 복원 및 결함 자동 복구 파이프라인 (Priority: P3)

사전 빌드 휠 복원(Tier 1~3) 실패 시 원자적 롤백 및 안전한 정리(uninstall)를 보장하여 불완전한 설치 상태로 서버가 가동되지 않도록 보호한다.

**Why this priority**: C++ 컴파일 실패나 휠 설치 실패 시 가상환경 오염을 방지하고 명확한 오류 로그를 제공하기 위함이다.

**Independent Test**: C++ 컴파일 중 강제 종료 또는 오류 발생 시 트랩(trap) 메커니즘이 동작하여 결함 패키지를 자동 제거하는지 테스트한다.

**Acceptance Scenarios**:

1. **Given** C++ 빌드 도중 시그널(ERR/INT/TERM) 또는 컴파일 에러가 발생할 때, **When** 트랩 메커니즘이 유발되면, **Then** 설치 시도 중이던 결함 패키지를 정리(uninstall)하고 사용자에게 명확한 해결 가이드를 출력한다.

---

### User Story 4 - NVIDIA 드라이버 및 CUDA Toolkit 자동 업데이트 스크립트 (Priority: P2)

시스템 관리자 및 사용자가 NVIDIA GPU 드라이버 및 CUDA Toolkit, cuDNN 버전을 간편하게 업데이트할 수 있도록 독립 헬퍼 스크립트(`scripts/update_cuda_drivers.sh`) 및 `setup.sh` 인라인 연동을 가동하여 원스톱 패키지 업데이트를 지원한다.

**Why this priority**: 호스트 패키지 미달 시 사용자가 복잡한 수동 APT 명령어 조합 대신 안전하게 정제된 스크립트로 최신 드라이버 및 CUDA 환경을 구축할 수 있게 하기 위함이다.

**Independent Test**: `sudo ./scripts/update_cuda_drivers.sh` 스크립트를 실행하거나 `setup.sh` 인라인 가동을 통해 호스트 OS 패키지 매니저(apt/dnf 등)를 거쳐 최신 권장 NVIDIA 드라이버 및 CUDA Toolkit이 정상 설치/업데이트되는지 확인한다.

**Acceptance Scenarios**:

1. **Given** 관리자 권한(`sudo`)이 부여된 환경에서, **When** `./scripts/update_cuda_drivers.sh` 또는 `setup.sh` 대화형 업데이트가 실행되면, **Then** 최신 호환 NVIDIA 드라이버 및 CUDA Toolkit, cuDNN을 탐지하여 패키지 설치를 안전하게 완수한다.

---

### Edge Cases

- **NVIDIA GPU 드라이버/nvcc/cuDNN 미설치 또는 버전 미달 시**: GPU 가속 빌드가 불가능하므로 CPU 전용 서빙으로 암묵적 폴백하지 않고 `setup.sh` 대화형 업데이트 또는 즉시 fail-fast 에러 및 `scripts/update_cuda_drivers.sh` 안내를 출력하고 중단해야 함.
- **uv 휠 캐시에 CPU 전용 바이너리가 유입된 경우**: 단순 `uv sync`가 무효한 휠을 재사용할 수 있으므로, 실측 검증 후 `--no-cache-dir` 플래그로 C++ 재컴파일을 강제해야 함.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 시스템은 llama.cpp 설치 후 반드시 GPU 가속 함수(`llama_supports_gpu_offload()`)의 반환값을 검증해야 한다.
- **FR-002**: 시스템은 GPU 가속 지원 검증 실패 시 기존 패키지를 제거하고 `-DGGML_CUDA=ON` 및 GPU 아키텍처 플래그가 포함된 동적 C++ 재컴파일을 수행해야 한다.
- **FR-003**: 시스템은 C++ 컴파일 또는 휠 검증 실패 시 가상환경 내 결함 패키지를 원자적으로 cleanup(uninstall)하여 가상환경 오염을 방지해야 한다.
- **FR-004**: 시스템은 호스트 하드웨어 특성(CPU SIMD 지원 여부, GPU Compute Capability)에 맞는 플랫폼 프로필을 매칭하고 이에 부합하는 CMAKE_ARGS를 자동 적용해야 한다.
- **FR-005**: 시스템은 필수 빌드 환경 요소(NVIDIA CUDA Toolkit `nvcc`, GPU 드라이버 `nvidia-smi`)의 존재 여부를 사전 점검하고 누락 시 즉시 실행을 중단(Fail-Fast)해야 한다.
- **FR-006**: 시스템은 `scripts/setup.sh` 및 `scripts/status_server.sh` 가동 시 NVIDIA Driver, CUDA Toolkit (`nvcc`), cuDNN 버전을 정밀 감지하고 llama.cpp 호환 최소 버전(Driver >= 525, CUDA >= 12.0, cuDNN >= 8.x) 및 최신 업데이트 필요 여부를 검증해야 한다.
- **FR-007**: 시스템은 GPU 드라이버/CUDA Toolkit/cuDNN 버전이 호환 최소 요구사항에 미달할 경우 버전 미달 경고 가이드를 명확히 출력해야 한다.
- **FR-008**: 시스템은 NVIDIA GPU 드라이버 및 CUDA Toolkit, cuDNN 패키지를 OS 패키지 매니저(apt/dnf 등)를 통해 원스톱으로 최신 권장 버전으로 자동 설치 및 업데이트하는 독립 헬퍼 스크립트(`scripts/update_cuda_drivers.sh`)를 제공해야 한다.
- **FR-009**: `scripts/setup.sh` 실행 중 호스트의 드라이버, CUDA Toolkit 또는 cuDNN 버전 미달이 감지되는 경우, 대화형 TTY 환경에서는 사용자 프롬프트 승인 후 `sudo apt-get` 기반 인라인 자동 패키지 업데이트를 진행해야 하며, 비대화형 환경에서는 수동 명령 안내 후 즉시 구동을 중단(Fail-Fast)해야 한다.

### Key Entities

- **LlamaBuildProfile**: CPU SIMD(AVX/AVX2/FMA/F16C) 및 GPU Compute Capability, CMAKE_ARGS 매핑 매개변수.
- **WheelValidationResult**: 휠 패키지 내 .so 바이너리의 AVX 명령어 포함 여부, CUDA 가속 함수 활성화 여부를 담은 검증 결과.
- **CudaEnvironmentInfo**: NVIDIA GPU 드라이버 버전, CUDA Toolkit(`nvcc`) 버전, cuDNN 라이브러리 버전 및 호환성 검증 상태.
- **CudaUpdateScript**: OS 패키지 관리자를 통해 NVIDIA 드라이버 및 CUDA Toolkit/cuDNN 최신 패키지를 원스톱으로 갱신하는 쉘 스크립트(`scripts/update_cuda_drivers.sh`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 이미 검증된 GPU 휠이 가상환경에 상주해 있을 경우 setup.sh의 휠 검증 단계는 0.1초 이내에 통과 및 스킵되어야 한다.
- **SC-002**: GPU 가속 미활성 패키지가 감지되면 100% 탐지하여 automatic failover C++ 재컴파일 단계로 진입해야 한다.
- **SC-003**: C++ 소스 재컴파일 완료 후 GPU 가속 검증 통과율 100%를 달성해야 한다.
- **SC-004**: C++ 빌드 실패 시 100% 정리(clean exit)되어 오염된 패키지가 가상환경에 남지 않아야 한다.
- **SC-005**: `setup.sh` 내 GPU 드라이버, CUDA Toolkit, cuDNN 버전 검증 정확도 100%를 달성하고, 버전 미달 시 대화형 승인 후 100% 인라인 자동 업데이트 및 비대화형 Fail-Fast를 완수해야 한다.
- **SC-006**: `scripts/update_cuda_drivers.sh` 및 `setup.sh` 실행 시 OS 패키지 관리자를 통해 NVIDIA 드라이버 및 CUDA Toolkit 자동 설치/업데이트 완료율 100%를 달성해야 한다.

## Assumptions

- 시스템 환경에는 NVIDIA GPU 및 CUDA Toolkit(nvcc) 환경이 준비되어 있거나, `scripts/setup.sh` 인라인 업데이트 및 `scripts/update_cuda_drivers.sh`를 통해 설치 가능하다.
- CPU 전용 폴백 서빙은 프로젝트 정책상 허용되지 않으며 GPU 가속이 필수적이다.
- uv 패키지 관리자가 설치되어 있으며 파이썬 가상환경(.venv)이 준비되어 있다.
