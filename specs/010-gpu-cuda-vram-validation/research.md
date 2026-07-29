# Technical Research: GPU/CUDA 하드웨어 가속 인식, VRAM 로드 검증 및 예외 처리 (GPU CUDA Acceleration & VRAM Load Validation)

**Feature Branch**: `010-gpu-cuda-vram-validation`
**Date**: 2026-07-29

---

## 1. NVIDIA GPU 및 CUDA 백엔드 자동 감지 방식 (GPU & CUDA Detection)

### Decision
`nvidia-smi` CLI 및 `pynvml` / `llama_cpp` C-API 헬퍼 함수를 조합하여 3단계 사전 하드웨어 검증기(`src/core/gpu_detector.py`)를 구현합니다.

### Rationale
- **1단계 (OS GPU H/W 검증)**: `nvidia-smi` 및 `pynvml`을 호출하여 시스템에 NVIDIA GPU(GeForce GTX 1080 Ti 11GB)가 존재하는지 확인.
- **2단계 (CUDA 가속 C-API 검증)**: `llama_cpp.llama_supports_gpu()` 또는 runtime dll C-API를 통해 `llama.cpp` 엔진이 CUDA 가속으로 빌드되었는지 점검.
- **3단계 (CPU 전용 차단)**: CPU 전용 바이너리 실행 시도가 감지되거나 CUDA 백엔드 인식 실패 시 프로세스 구동을 즉각 차단하고 `GpuAccelerationError`를 던짐.

---

## 2. VRAM 100% 레이어 오프로드 실시간 검증 (VRAM 100% Offload Verification)

### Decision
`llama-server` 서브프로세스의 `stdout`/`stderr` 출력을 실시간 스트리밍 인터셉트하여 `llm_load_tensors: offloaded X/Y layers to GPU` 및 `VRAM` 점유 로그를 파싱하고, `offloaded_layers == total_layers` 비율을 검증합니다.

### Rationale
- 일부 레이어가 CPU RAM으로 튕겨나가거나 혼용되는 경우 `is_fully_offloaded=False`로 판정.
- 전체 레이어가 VRAM에 탑재되지 않으면 `VramOverflowError` 또는 `GpuAccelerationError`를 명시적으로 던져 서빙 개설을 거부함.

---

## 3. 예외 처리 체계 및 목업 정제 (Exception Hierarchy & Mock Cleanup)

### Decision
- **예외 클래스 정의**:
  - `GpuAccelerationError`: GPU 미감지, CUDA 백엔드 미지원, CPU 바이너리 감지 시 발생.
  - `VramOverflowError`: VRAM 부족으로 인한 레이어 강제 CPU 롤백 발생 시 발생.
- **목업 제거 및 전수 리팩토링**:
  - `src/core/`, `src/eval/`, `scripts/` 전반의 더미 fallback 응답, 하드코딩된 품질 점수 및 미사용 임포트를 전수 조사하여 제거하고 100% 실제 GPU/CUDA 런타임 추론 로직으로 교체함.

---

## 4. Alternatives Considered

- **더미 Fallback 데이터 유지**: GPU 오류 발생 시 더미 응답으로 우회하는 방식을 고려하였으나, 실무 환경에서 왜곡된 결과를 제공하므로 완전히 거부함.
