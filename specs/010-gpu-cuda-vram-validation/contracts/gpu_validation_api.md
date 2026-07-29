# API Contract: GPU & VRAM Offload Validation Interface

**Feature Branch**: `010-gpu-cuda-vram-validation`
**Date**: 2026-07-29

---

## 1. GpuDetector Interface (`src/core/gpu_detector.py`)

### `check_gpu_availability() -> GpuDeviceInfo`
NVIDIA GPU 및 CUDA 가속 백엔드 존재 여부를 점검합니다.
- **Returns**: `GpuDeviceInfo`
- **Raises**: `GpuAccelerationError` (GPU 미존재 또는 CPU-only 바이너리 감지 시)

---

## 2. Server Status API Contract (`GET /v1/status`)

```json
{
  "state": "READY",
  "current_model": "qwen3.5-2b",
  "gpu_info": {
    "device_name": "NVIDIA GeForce GTX 1080 Ti",
    "total_vram_mb": 11264,
    "free_vram_mb": 8500,
    "is_cuda_available": true
  },
  "offload_status": {
    "total_layers": 28,
    "offloaded_layers": 28,
    "is_fully_offloaded": true,
    "offloaded_vram_mb": 3000
  }
}
```
