# Data Model & Schema Specifications: make_seed_pack.sh 레거시 사전 휠 Post-Build AVX 실측 검증 로직 및 빌드 플래그 정밀화 (059-fix-legacy-wheel-avx-build)

**Feature Branch**: `059-fix-legacy-wheel-avx-build`  
**Date**: 2026-07-31  
**Spec Link**: [`spec.md`](file:///home/dev/storage/vllm_serv/specs/059-fix-legacy-wheel-avx-build/spec.md)

---

## Data Entities & Schema Definition

### 1. WheelVerificationResult (바이너리 검증 결과 데이터 객체)

`scripts/verify_wheel_binary.py` 검증 도구가 `.whl` 파이썬 패키지를 아카이빙 해제 및 정밀 스캔하여 생성하는 결과 데이터 구조입니다.

| Attribute Field | Type | Required | Description |
|---|---|---|---|
| `wheel_path` | String | Yes | 검증 대상 `.whl` 파일 경로 |
| `is_valid` | Boolean | Yes | 최종 검증 통과 여부 (CUDA 활성화 & CPU 호스트 AVX 무결성 통과 시 True) |
| `cuda_enabled` | Boolean | Yes | CUDA GPU 가속 디바이스 라이브러리(`ggml-cuda.so`) 존재 여부 |
| `avx_clean` | Boolean | Yes | CPU 호스트 라이브러리(`ggml-cpu.so`, `libllama.so` 등)의 AVX 명령어 0건 여부 |
| `cpu_so_counts` | Map<String, Int> | Yes | CPU 호스트 `.so` 파일별 검출된 AVX 명령어 카운트 |
| `cuda_so_files` | List<String> | Yes | 스캔에서 CUDA 디바이스 커널로 판별/구분된 `.so` 파일 목록 |
| `message` | String | Yes | 인세션 인간 읽기 가능한 실측 결과 요약 메세지 |

---

### 2. LegacyWheelBuildConfig (사전 휠 빌드 구성 정보)

`scripts/make_seed_pack.sh`에서 레거시 i7-930 타깃 사전 휠 컴파일 시 사용하는 컴파일 및 환경 구성 스키마입니다.

| Attribute Field | Value / Format | Description |
|---|---|---|
| `target_profile` | `legacy-i7-930-gtx1070` | Nehalem CPU + GTX 1070 타깃 프로필 ID |
| `cflags` | `-march=x86-64` | 기본 x86-64 호환 C/C++ 컴파일러 플래그 |
| `skbuild_cmake_args` | `-DGGML_CUDA=ON -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_F16C=OFF -DGGML_FMA=OFF -DGGML_NATIVE=OFF -DCMAKE_CUDA_ARCHITECTURES=61` | `scikit-build-core` 및 CMake 전달 인자 |
| `wheel_dir` | `wheels/legacy_i7_930` | 사전 빌드 휠 아티팩트 저장 디렉터리 경로 |
