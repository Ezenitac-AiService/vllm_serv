# Phase 0 Research: CPU 빌드 감지 및 다중 플랫폼 지원 (llama.cpp)

**Feature Branch**: `020-cpu-build-detection`  
**Date**: 2026-07-30  
**Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/020-cpu-build-detection/spec.md)

---

## 1. 개요 및 연구 목표

본 연구는 i7 930(Nehalem 아키텍처, SSE4.2 전용)과 같은 레거시 CPU 환경 및 GTX 1070(Pascal, `sm_61`)과 같은 다중 GPU 아키텍처 환경에서 `llama.cpp` 네이티브 컴파일(`llama-server`) 및 `llama-cpp-python` pip 패키지 컴파일이 명령어 세트 비호환(예: `Illegal instruction`) 없이 성공적으로 수행되도록 하는 하드웨어 자동 감지 및 CMake 플래그 동적 생성 메커니즘을 설계하기 위해 수행되었습니다.

---

## 2. 주요 연구 과제 및 해결 방안

### 과제 1: 리눅스 환경에서 CPU 명령어 세트 자동 감지 메커니즘
- **문제점**: llama.cpp는 기본 컴파일 시 컴파일러가 지원하는 최신 명령어 세트(AVX, AVX2, F16C, FMA 등)를 활성화하도록 설정되어 있어, i7 930과 같은 구형 CPU(AVX 미지원)에서 컴파일/실행 시 `Illegal instruction` SIGILL 런타임 크래시가 발생함.
- **연구 옵션**:
  1. `/proc/cpuinfo` 분석 (Linux 전용 파싱)
  2. Python `platform` / `cpuid` 모듈 활용
  3. C/C++ 소규모 테스트 바이너리 컴파일 실행 검사
- **결정 (Decision)**: **`/proc/cpuinfo` 분석 및 `sysctl` (macOS/cross-platform) 폴백을 갖춘 순수 Python 하드웨어 감지 모듈(`src/core/cpu_detector.py`) 구현**
- **근거**:
  - 프로젝트 타겟 플랫폼이 Ubuntu Server 24.04 LTS이므로 `/proc/cpuinfo`의 `flags` 필드를 직접 파싱하는 것이 외래 의존성 없이 가장 빠르고 정확함.
  - 감지 대상 핵심 CPU 키워드:
    - `avx` → `GGML_AVX` (ON/OFF)
    - `avx2` → `GGML_AVX2` (ON/OFF)
    - `f16c` → `GGML_F16C` (ON/OFF)
    - `fma` → `GGML_FMA` (ON/OFF)
    - `sse4_2` 또는 `sse4_1` → 기본 SSE 활성화
- **폴백 정책**: `/proc/cpuinfo` 접근 불가능 시 최상위 안전 모드(AVX/AVX2/F16C/FMA 모두 `OFF`)로 설정하여 절대 `Illegal instruction`이 발생하지 않도록 조치.

---

### 과제 2: llama.cpp CMake 빌드 옵션 매핑
- **문제점**: llama.cpp의 CMake 빌드 옵션과 `llama-cpp-python` 설치 시 전파해야 하는 `CMAKE_ARGS` 플래그 간 매핑 정합성 필요.
- **연구 결과**:
  - `llama.cpp` (ggml) CMake 핵심 인자:
    - `-DGGML_AVX=ON|OFF`
    - `-DGGML_AVX2=ON|OFF`
    - `-DGGML_F16C=ON|OFF`
    - `-DGGML_FMA=ON|OFF`
    - `-DGGML_CUDA=ON`
    - `-DCMAKE_CUDA_ARCHITECTURES=<arch>` (예: `61` for GTX 1070, `86` for RTX 3060)
- **적용 대상**:
  1. `setup.sh`: `CMAKE_ARGS="$(uv run python -m src.core.cpu_detector --format cmake)" uv pip install "llama-cpp-python[server]" ...`
  2. `src/core/process_manager.py`: `verify_and_build_llama_server()` 함수 실행 시 `cpu_detector.get_cmake_args()` 결과를 `cmake -B build ...` 인수로 전달.

---

### 과제 3: GPU Compute Capability 자동 감지 및 CUDA 아키텍처 타겟 지정
- **문제점**: Pascal 아키텍처(GTX 1070, compute capability 6.1)와 Ampere 아키텍처(RTX 3060, compute capability 8.6) 간 CUDA 소스 컴파일 시 적절한 `-DCMAKE_CUDA_ARCHITECTURES` 설정 필요.
- **연구 결과**:
  - `nvidia-smi --query-gpu=compute_cap --format=csv,noheader,nounits` 명령을 실행하여 `6.1` -> `61`, `8.6` -> `86` 문자열 추출.
  - 추출된 값은 CMake 옵션 `-DCMAKE_CUDA_ARCHITECTURES=61` 또는 `-DCMAKE_CUDA_ARCHITECTURES=86`으로 변환됨.
  - GPU 감지 실패 시 기존 프로젝트 헌장 및 명세(FR-009)에 따라 fail-fast로 빌드 중단 (`GpuAccelerationError`).

---

### 과제 4: 타겟 플랫폼 프로필 관리 체계 (`config/platform_profiles.json`)
- **연구 옵션**:
  1. 하드코딩된 Python 딕셔너리
  2. JSON 기반 프로필 파일
- **결정 (Decision)**: **`config/platform_profiles.json` 파일 생성 및 `ConfigManager` 통합**
- **근거**:
  - 개발 환경(RTX 3060 + Modern CPU)과 레거시 서버(i7 930 + GTX 1070 + 24GB RAM) 사양을 명시적인 JSON 객체로 정의하여 유지보수성 및 확장성 확보.

---

## 3. 요약 및 최종 결정

| 항목 | 선택된 방안 | 비고 |
|------|-------------|------|
| **CPU 감지 방식** | `/proc/cpuinfo` 기반 `src/core/cpu_detector.py` 모듈 | 실패 시 보수적 폴백(All OFF) |
| **CMake 플래그 조율** | `-DGGML_AVX`, `-DGGML_AVX2`, `-DGGML_F16C`, `-DGGML_FMA` 동적 지정 | 네이티브 & pip 양쪽 적용 |
| **CUDA Arch 지정** | `nvidia-smi`를 통한 compute capability (`61`, `86`) 추출 후 `-DCMAKE_CUDA_ARCHITECTURES` 주입 | 단일 아키텍처 타겟 |
| **프로필 관리** | `config/platform_profiles.json` 및 `ConfigManager` | 하드웨어 사양 중앙 등록 |
