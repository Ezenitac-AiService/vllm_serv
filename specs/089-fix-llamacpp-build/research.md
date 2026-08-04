# Research: llama.cpp 빌드 검증 및 휠 컴파일 파이프라인 (089-fix-llamacpp-build)

## Overview & Research Objectives

본 문서는 `llama.cpp` (llama-cpp-python) 패키지의 CUDA GPU 가속 컴파일 검증, CPU-only 휠 자동 캐시 무효화, NVIDIA Driver / CUDA Toolkit / cuDNN 버전 검증 및 `setup.sh` 인라인 자동 패키지 업데이트 파이프라인 수립을 위한 기술적 연구 결과를 정리합니다.

---

## Technical Research & Decisions

### 1. `llama-cpp-python` CUDA C++ 컴파일 및 uv 캐시 무효화

- **Decision**: `CMAKE_ARGS="-DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=86 ..."` 환경 변수와 함께 `uv pip install --no-cache-dir "llama-cpp-python[server]" --no-binary llama-cpp-python` 명령어로 C++ 소스 재컴파일을 유발합니다.
- **Rationale**: `uv`는 빌드 시 캐시된 휠을 재사용하는 특성이 있습니다. 이전 컴파일에서 CPU 전용 바이너리로 빌드된 휠이 캐시에 존재하는 경우 `uv pip install`이 CMAKE_ARGS를 무시하고 기존 캐시 휠을 고속 복사하므로, `verify_wheel_binary.py` 검증 실패 시 `--no-cache-dir` 플래그로 캐시 무효화를 강제해야 합니다.
- **Alternatives Considered**:
  - `pip cache purge`: 전체 pip/uv 캐시 삭제는 다른 무관한 패키지 캐시까지 날려 동기화 속도를 떨어뜨림. `--no-cache-dir` 단일 지정이 가장 원자적임.

### 2. NVIDIA Driver, CUDA Toolkit, cuDNN 버전 탐지 및 기준

- **Decision**:
  - **NVIDIA Driver**: `nvidia-smi --query-gpu=driver_version --format=csv,noheader` 파싱 (최소 기준: >= 525.00, 권장: 550+).
  - **CUDA Toolkit (`nvcc`)**: `nvcc --version | grep release` 파싱 (최소 기준: >= 12.0, 현 시스템: CUDA 12.8).
  - **cuDNN**: `python3 -c "import torch; print(torch.backends.cudnn.version())"` 또는 `/usr/include/cudnn_version.h` / `/usr/local/cuda/include/cudnn_version.h` 파싱 (최소 기준: >= 8.9.0).
- **Rationale**: CUDA 12.x 대역에서 `llama.cpp` CUDA 그래픽 커널이 호환되며, RTX 3060 등 Ampere 계열(sm_86) 이상의 GPU 컴퓨트 능력을 100% 지원합니다.

### 3. `setup.sh` 인라인 자동 업데이트 & `scripts/update_cuda_drivers.sh`

- **Decision**:
  - `scripts/update_cuda_drivers.sh` 독립 헬퍼 스크립트를 작성하여 Ubuntu/Debian (`apt-get`) 및 RHEL/Rocky (`dnf`) 기반 시스템의 NVIDIA 공식 저장소 PPA / CUDA 배포판 갱신을 원스톱 처리.
  - `setup.sh` 실행 중 버전 미달 탐지 시 대화형 TTY (`[ -t 0 ]`) 환경이면 사용자 확인(`read -p`) 후 `sudo ./scripts/update_cuda_drivers.sh`를 인라인 자동 실행.
  - 비대화형(CI/CD) 환경일 경우 수동 안내 로그 출력 후 Fail-Fast (`exit 1`) 종료.
- **Rationale**: 서버 시스템 패키지 갱신 시 무단 갱신으로 인한 인프라 장애를 방지하면서도, 개발자 대화형 터미널에서의 편의성을 극대화합니다.

### 4. 휠 바이너리 3중 정합성 검증 (`verify_wheel_binary.py`)

- **Decision**:
  - `llama_supports_gpu_offload()` / `llama_supports_gpu()` 함수 반환값이 `True`인지 런타임 확인.
  - ZIP 아카이브 내 `.so` Shared Library 중 `ggml-cuda` 또는 `cuda` 라이브러리의 존재 여부 확인.
  - 호스트 CPU에 AVX가 없는 경우(Nehalem 등) ELF `objdump` 스캔으로 호스트 CPU .so 내 AVX 명령어 수 0개 검증.
- **Rationale**: CPU 전용 암묵적 폴백을 방지하고 GPU 오프로딩이 100% 가동되는 바이너리만 통과시킵니다.
