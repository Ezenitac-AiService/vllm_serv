# Data Model: CPU 빌드 감지 및 플랫폼 프로필

**Feature Branch**: `020-cpu-build-detection`  
**Date**: 2026-07-30  
**Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/020-cpu-build-detection/spec.md)

---

## Key Entities

### 1. CpuFeatureInfo (CPU 기능 정보)

호스트 시스템의 CPU 하드웨어 사양 및 지원 명령어 세트 정보 개체 (Pydantic Model).

- **`model_name`** (`str`): CPU 모델명 (예: `"Intel(R) Core(TM) i7 CPU 930 @ 2.80GHz"`)
- **`architecture`** (`str`): CPU 아키텍처 (예: `"x86_64"`)
- **`vendor_id`** (`str`): 제자사 ID (예: `"GenuineIntel"`)
- **`flags`** (`List[str]`): 지원되는 명령어 세트 플래그 리스트 (예: `["sse4_1", "sse4_2", "ssse3"]`)
- **`supports_sse4_2`** (`bool`): SSE4.2 지원 여부
- **`supports_avx`** (`bool`): AVX 지원 여부
- **`supports_avx2`** (`bool`): AVX2 지원 여부
- **`supports_f16c`** (`bool`): F16C 지원 여부
- **`supports_fma`** (`bool`): FMA 지원 여부
- **`is_fallback`** (`bool`): CPU 감지 실패에 따른 보수적 폴백 모드 여부

---

### 2. GpuCapabilityInfo (GPU 및 CUDA 아키텍처 정보)

호스트 시스템에 장착된 NVIDIA GPU의 Compute Capability 및 아키텍처 번호 개체 (Pydantic Model).

- **`gpu_name`** (`str`): GPU 모델명 (예: `"NVIDIA GeForce GTX 1070"`)
- **`compute_capability`** (`str`): CUDA compute capability 버전을 표현하는 문자열 (예: `"6.1"`, `"8.6"`)
- **`cuda_arch_code`** (`str`): CMake 인자로 사용될 2자리 코드 (예: `"61"`, `"86"`)
- **`total_vram_mb`** (`int`): VRAM 총 용량 (MB)

---

### 3. LlamaCppBuildFlags (llama.cpp 빌드 플래그 세트)

CPU 및 GPU 감지 결과에 따라 최종 결정된 CMake 빌드 옵션 개체 (Pydantic Model).

- **`ggml_cuda`** (`bool`): CUDA 가속 활성화 여부 (항상 `True`)
- **`ggml_avx`** (`bool`): AVX 플래그 (`-DGGML_AVX=ON|OFF`)
- **`ggml_avx2`** (`bool`): AVX2 플래그 (`-DGGML_AVX2=ON|OFF`)
- **`ggml_f16c`** (`bool`): F16C 플래그 (`-DGGML_F16C=ON|OFF`)
- **`ggml_fma`** (`bool`): FMA 플래그 (`-DGGML_FMA=ON|OFF`)
- **`cuda_architectures`** (`Optional[str]`): CMake CUDA 아키텍처 지정자 (예: `"61"`, `"86"`)
- **`cmake_args_list`** (`List[str]`): `["-DGGML_CUDA=ON", "-DGGML_AVX=OFF", ...]` 형태의 파이썬 리스트
- **`cmake_args_str`** (`str`): `-DGGML_CUDA=ON -DGGML_AVX=OFF ...` 형태의 쉘 전달용 단일 문자열

---

### 4. TargetPlatformProfile (타겟 플랫폼 프로필)

프로젝트에서 공식 지원하고 관리하는 플랫폼 사양 정의 객체 (`config/platform_profiles.json`).

- **`profile_id`** (`str`): 프로필 키 (예: `"i7-930-gtx1070"`, `"dev-rtx3060"`)
- **`name`** (`str`): 사람이 읽기 쉬운 플랫폼 이름
- **`cpu_model`** (`str`): 표준 CPU 명칭
- **`ram_gb`** (`int`): 시스템 RAM 용량 (GB)
- **`gpu_name`** (`str`): GPU 모델 명칭
- **`vram_mb`** (`int`): VRAM 용량 (MB)
- **`compute_capability`** (`str`): GPU Compute Capability
- **`os_name`** (`str`): 운영체제 이름 및 버전 (예: `"Ubuntu Server 24.04 LTS"`)
- **`expected_avx`** (`bool`): 해당 프로필의 예상 AVX 지원 여부
