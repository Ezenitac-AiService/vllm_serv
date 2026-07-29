# Data Model: Automated CUDA-Enabled llama.cpp Build & Setup Pipeline

## Key Entities & Schemas

### 1. CudaBuildPipeline

`setup.sh` 및 `ProcessManager`에서 CUDA 가속 빌드 플래그(`GGML_CUDA=on`)를 관리하는 빌드 구성 파이프라인엔티티.

| Field Name | Type | Description | Constraints |
|------------|------|-------------|-------------|
| `is_cuda_available` | `bool` | `nvcc` 및 `nvidia-smi` 감지 여부 | Mandatory |
| `cuda_version` | `Optional[str]` | CUDA Toolkit 버전 (예: "12.2") | Optional |
| `build_flags` | `List[str]` | CMake 및 pip 컴파일 주입 플래그 (`-DGGML_CUDA=ON`) | Mandatory |
| `llama_supports_gpu` | `bool` | `llama_cpp.llama_supports_gpu()` 검증 결과 | Must be `True` |

---

### 2. CudaEnvironmentCheck

CUDA 개발 환경 및 드라이버 존재 여부를 검증하는 엔티티.

| Field Name | Type | Description | Validation |
|------------|------|-------------|------------|
| `nvcc_path` | `Optional[str]` | `/usr/bin/nvcc` 또는 `PATH` 내 경로 | Must exist for build |
| `nvidia_smi_path` | `Optional[str]` | `nvidia-smi` 바이너리 경로 | Must exist for VRAM check |
| `vram_total_mb` | `int` | 총 VRAM 메모리 용량 (MB) | > 0 |

---

### 3. VramAllocationMonitor

`nvidia-smi` 및 `nvtop`에 인퍼런스 프로세스 PID 및 VRAM 실사용량이 등록되어 모니터링되는지 검증하는 엔티티.

| Field Name | Type | Description | Validation |
|------------|------|-------------|------------|
| `pid` | `int` | `llama-server` 또는 `python` 프로세스 PID | Active PID |
| `used_vram_mb` | `int` | GPU에 할당된 가중치 VRAM (MB) | > 2000MB (Model Resident) |
| `gpu_utilization_pct` | `float` | GPU 계산 코어 사용률 (%) | 0.0 ~ 100.0 |
