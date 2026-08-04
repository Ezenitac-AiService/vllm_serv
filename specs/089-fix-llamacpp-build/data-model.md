# Data Model: llama.cpp 빌드 검증 및 휠 컴파일 파이프라인 (089-fix-llamacpp-build)

## Entities & Schemas

### 1. `CudaEnvironmentInfo`

NVIDIA GPU 드라이버, CUDA Toolkit, cuDNN 라이브러리 버전 및 호환성 검증 상태를 나타내는 데이터 모델입니다.

| Attribute | Type | Description | Example / Constraints |
|-----------|------|-------------|-----------------------|
| `driver_version` | String | NVIDIA GPU 드라이버 버전 | `"595.84"` (최소 >= 525.0) |
| `cuda_toolkit_version` | String | nvcc CUDA Toolkit 버전 | `"12.8"` (최소 >= 12.0) |
| `cudnn_version` | String | cuDNN 라이브러리 버전 | `"9.1.0"` (최소 >= 8.9.0) |
| `is_driver_compatible` | Boolean | 드라이버 최소 호환 기준 통과 여부 | `True` |
| `is_cuda_compatible` | Boolean | CUDA Toolkit 최소 호환 기준 통과 여부 | `True` |
| `is_cudnn_compatible` | Boolean | cuDNN 최소 호환 기준 통과 여부 | `True` |
| `update_required` | Boolean | 업데이트 필요 여부 | `False` |

---

### 2. `LlamaBuildProfile`

호스트 CPU SIMD 세트 및 GPU Compute Capability, 동적 CMAKE 인자 매핑 정보를 나타내는 모델입니다.

| Attribute | Type | Description | Example / Constraints |
|-----------|------|-------------|-----------------------|
| `profile_name` | String | 매칭된 플랫폼 프로필 명칭 | `"dev-rtx3060"` |
| `cpu_model` | String | 호스트 CPU 모델명 | `"Intel(R) Core(TM) i7-4770 CPU"` |
| `supports_avx` | Boolean | CPU AVX 지원 여부 | `True` |
| `supports_avx2` | Boolean | CPU AVX2 지원 여부 | `True` |
| `supports_fma` | Boolean | CPU FMA 지원 여부 | `True` |
| `supports_f16c` | Boolean | CPU F16C 지원 여부 | `True` |
| `gpu_name` | String | GPU 모델명 | `"NVIDIA GeForce RTX 3060"` |
| `compute_capability` | String | Compute Capability (arch_code) | `"8.6"` (`sm_86`) |
| `cmake_args` | String | 동적 파싱 CMAKE_ARGS 문자열 | `"-DGGML_CUDA=ON -DGGML_AVX=ON ..."` |

---

### 3. `WheelValidationResult`

파이썬 가상환경 또는 .whl 파일 내 Shared Library의 CUDA 활성화 및 SIMD 정합성 검증 결과 모델입니다.

| Attribute | Type | Description | Example / Constraints |
|-----------|------|-------------|-----------------------|
| `is_valid` | Boolean | 검증 통과 여부 | `True` / `False` |
| `cuda_enabled` | Boolean | `llama_supports_gpu_offload()` GPU 가속 활성화 여부 | `True` |
| `has_cuda_so` | Boolean | .whl 내 `ggml-cuda.so` 등 CUDA 기기 라이브러리 탑재 여부 | `True` |
| `cpu_avx_instruction_count` | Integer | 호스트 CPU .so 내 AVX 명령어 수 | `0` (AVX 미지원 CPU 환경) |
| `error_message` | String | 검증 실패 시 원인 로그 | `"llama_supports_gpu_offload() returned False"` |

---

### 4. `CudaUpdateScript`

OS 패키지 관리자를 통해 NVIDIA 드라이버 및 CUDA Toolkit/cuDNN 패키지를 인라인/원스톱 갱신하는 쉘 스크립트 실행 모델입니다.

| Attribute | Type | Description | Example / Constraints |
|-----------|------|-------------|-----------------------|
| `script_path` | String | 업데이트 헬퍼 스크립트 경로 | `"scripts/update_cuda_drivers.sh"` |
| `os_type` | String | 감지된 OS 분류 | `"ubuntu"`, `"debian"`, `"rhel"`, `"rocky"` |
| `execution_mode` | String | 실행 모드 | `"interactive"` (TTY), `"non-interactive"` |
| `sudo_acquired` | Boolean | sudo 관리자 권한 확보 여부 | `True` |
