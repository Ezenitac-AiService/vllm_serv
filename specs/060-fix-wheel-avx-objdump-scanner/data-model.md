# Data Model: 060-fix-wheel-avx-objdump-scanner

## Entities & Schemas

### 1. `WheelVerificationResult` (바이너리 검증 결과 모델)

| Field Name | Type | Description | Constraints |
|------------|------|-------------|-------------|
| `is_valid` | `bool` | 전체 검증 통과 여부 | `True` for Exit Code 0 |
| `cpu_so_counts` | `Dict[str, int]` | CPU 호스트 `.so` 파일별 실제 AVX 명령어 개수 | `total == 0` when `avx_clean=True` |
| `cuda_enabled` | `bool` | CUDA 디바이스 커널 포함 여부 | Must be `True` for GPU wheels |
| `message` | `str` | 실측 검증 요약 레포트 문자열 | e.g. `✓ Wheel verified valid: CUDA enabled...` |

### 2. `LegacyWheelBuildConfig` (레거시 사전 컴파일 휠 설정)

| Field Name | Type | Description | Values |
|------------|------|-------------|--------|
| `CFLAGS` | `str` | C 컴파일러 플래그 | `-march=x86-64` |
| `CXXFLAGS` | `str` | C++ 컴파일러 플래그 | `-march=x86-64` |
| `SKBUILD_CMAKE_ARGS` | `str` | scikit-build-core 전파용 CMake 플래그 | `-DGGML_CUDA=ON -DGGML_NATIVE=OFF -DGGML_AVX=OFF...` |
