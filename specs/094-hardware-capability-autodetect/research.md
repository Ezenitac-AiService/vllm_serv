# Research & Technical Decisions: 3대 멀티 플랫폼 HW 차등 감지 및 훈련 플랫폼(RTX 3060) 최적 하드웨어 가속 자동 설정 (`094-hardware-capability-autodetect`)

## Phase 0: Research & Decision Log

### Decision 1: CPU AVX2 유무 & GPU Compute Capability 2원 축 탐지 파이프라인 수립

- **Decision**: `src/core/cpu_detector.py` 및 `scripts/common.sh`에 `/proc/cpuinfo` (또는 Windows/macOS 호환 API)의 `avx2` / `avx` CPU 플래그와 `nvidia-smi` / `torch` / `nvcc` 기반 GPU Compute Capability (`sm_61` vs `sm_86`)를 동시 스캔하는 믹스인을 수립한다.
- **Rationale**:
  - i7-930 (Nehalem, SSE4.2) 서비스 플랫폼에서의 `-mavx2` 휠 컴파일 및 가동으로 인한 `SIGILL (Illegal Instruction)` 파손 방지.
  - GTX 1080Ti / GTX 1070 (Pascal, `sm_61`)에서의 미지원 FlashAttention-2 / BF16 호출 크래시 방지 및 FP16 / SDPA 자동 하향 호환.
  - RTX 3060 (Ampere, `sm_86`) 훈련 플랫폼에서의 3세대 Tensor Cores, TF32, BF16, FlashAttention-2 (`LLAMA_FLASH_ATTN=ON`) 100% 활성화.

---

### Decision 2: C++ CMAKE_ARGS 동적 주입 및 FlashAttention-2 안전 폴백

- **Decision**: `scripts/setup.sh`의 llama-cpp-python 동적 재컴파일 시 `CMAKE_ARGS` 플래그를 하드웨어 감지 결과에 맞춰 생성한다:
  - **Nehalem (i7-930)**: `CMAKE_ARGS="-DGGML_AVX2=OFF -DGGML_AVX=OFF -DGGML_FMA=OFF -DGGML_CUDA=ON"`
  - **Pascal (sm_61)**: `CMAKE_ARGS="-DGGML_CUDA=ON -DGGML_AVX2=ON -DGGML_FLASH_ATTN=OFF"`
  - **Ampere (sm_86)**: `CMAKE_ARGS="-DGGML_CUDA=ON -DGGML_AVX2=ON -DGGML_FLASH_ATTN=ON -DGGML_CUDA_FA_ALL=ON"`
- **Rationale**:
  - 호스트 스펙에 최적화된 바이너리를 동적 생성하고 미지원 커널 실패 시 SDPA로 안전 폴백.

---

### Decision 3: 단위 테스트 환경 모의 격리 (Mock Injection Pattern)

- **Decision**: `tests/unit/test_hardware_autodetect.py`에 `patch.dict(os.environ, {"MOCK_COMPUTE_CAPABILITY": "8.6", "MOCK_CPU_AVX2": "1"})`를 제공하여 단일 테스트 서버에서도 3대 플랫폼(개발/서비스/훈련) 전 구역 탐지 및 파라미터 분기를 100% 검증한다.
