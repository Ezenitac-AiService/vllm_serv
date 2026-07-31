# Contract: CPU & GPU Detector Python Module & CLI API

**Feature Branch**: `020-cpu-build-detection`  
**Date**: 2026-07-30

---

## 1. CLI Interface (`python -m src.core.cpu_detector`)

### Command Options

```bash
uv run python -m src.core.cpu_detector [OPTIONS]
```

- `--format cmake`: 쉘 스크립트(`setup.sh`)에서 `CMAKE_ARGS`로 즉시 활용 가능한 한 줄 문자열 출력.
  - 예시 (i7 930 + GTX 1070): `-DGGML_CUDA=ON -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_F16C=OFF -DGGML_FMA=OFF -DCMAKE_CUDA_ARCHITECTURES=61`
  - 예시 (RTX 3060 + Modern CPU): `-DGGML_CUDA=ON -DGGML_AVX=ON -DGGML_AVX2=ON -DGGML_F16C=ON -DGGML_FMA=ON -DCMAKE_CUDA_ARCHITECTURES=86`
- `--format json`: 전체 감지 정보(CPU, GPU, 빌드 플래그)를 JSON 포맷으로 출력.
- `--report`: 사람이 읽기 쉬운 요약 로그 출력 (기본값).

---

## 2. Python Module API (`src/core/cpu_detector.py`)

### `detect_cpu_features() -> CpuFeatureInfo`
- 호스트 CPU의 명령어 세트를 감지하여 `CpuFeatureInfo` 객체 반환.

### `detect_gpu_capability() -> GpuCapabilityInfo`
- 호스트 GPU의 Compute Capability를 감지하여 `GpuCapabilityInfo` 객체 반환.
- 감지 실패 시 `GpuAccelerationError` 발생.

### `get_llama_build_flags() -> LlamaCppBuildFlags`
- CPU 및 GPU 감지 결과를 통합하여 `LlamaCppBuildFlags` 객체 반환.

---

## 3. Configuration Contract (`config/platform_profiles.json`)

```json
{
  "dev-rtx3060": {
    "name": "Primary Development Workstation",
    "cpu_model": "Modern x86_64 CPU",
    "ram_gb": 32,
    "gpu_name": "NVIDIA GeForce RTX 3060",
    "vram_mb": 12288,
    "compute_capability": "8.6",
    "os_name": "Linux x86_64",
    "expected_avx": true
  },
  "legacy-i7-930-gtx1070": {
    "name": "Legacy Target Server (i7 930)",
    "cpu_model": "Intel Core i7 930 @ 2.80GHz",
    "ram_gb": 24,
    "gpu_name": "NVIDIA GeForce GTX 1070",
    "vram_mb": 8192,
    "compute_capability": "6.1",
    "os_name": "Ubuntu Server 24.04 LTS",
    "expected_avx": false
  }
}
```
