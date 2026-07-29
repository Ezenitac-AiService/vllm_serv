# Data Model: GPU/CUDA 하드웨어 가속 인식, VRAM 로드 검증 및 예외 처리

**Feature Branch**: `010-gpu-cuda-vram-validation`
**Date**: 2026-07-29

---

## 1. Entities & Data Structures

### A. GpuDeviceInfo (Pydantic v2 Model)
GPU 하드웨어 및 CUDA 환경 감지 정보 엔티티.

- **device_id** (`int`): GPU 디바이스 인덱스 (기본 `0`)
- **name** (`str`): GPU 제품명 (예: `'NVIDIA GeForce GTX 1080 Ti'`)
- **total_vram_mb** (`int`): 총 VRAM 용량 (MB 단위, 예: `11264`)
- **free_vram_mb** (`int`): 현재 사용 가능한 여유 VRAM 용량 (MB 단위)
- **driver_version** (`str`): NVIDIA 드라이버 버전 (예: `'580.173.02'`)
- **cuda_version** (`str`): CUDA 런타임 버전 (예: `'13.0'`)
- **is_cuda_available** (`bool`): CUDA 가속 사용 가능 여부

### B. VramOffloadStatus (Pydantic v2 Model)
서빙 프로세스의 VRAM 레이어 오프로딩 검증 엔티티.

- **model_id** (`str`): 모델 식별자 (예: `'qwen3.5-2b'`)
- **total_layers** (`int`): 모델의 전체 트랜스포머 레이어 수
- **offloaded_layers** (`int`): GPU VRAM에 오프로드된 레이어 수
- **is_fully_offloaded** (`bool`): 100% VRAM 오프로드 성공 여부 (`offloaded_layers == total_layers`)
- **offloaded_vram_mb** (`int`): VRAM에 점유된 메모리 크기 (MB)
- **has_clip_offload** (`Optional[bool]`): Gemma 4 멀티모달 CLIP 가중치 VRAM 오프로드 성공 여부

---

## 2. Exceptions Hierarchy

```text
Exception
└── GpuValidationError
    ├── GpuAccelerationError     (GPU 미감지, CPU-only 바이너리 실행 시 차단)
    └── VramOverflowError        (VRAM 부족으로 인한 일부 레이어 CPU 롤백 발생 시 차단)
```

---

## 3. State Transitions

```text
[UNLOADED] ──(GPU & CUDA Scan)──> [GPU_VERIFIED] ──(Full VRAM Offload Check)──> [READY]
                                      │                                             │
                                 (GPU/CUDA Fail)                               (Partial Offload)
                                      ▼                                             ▼
                             [GpuAccelerationError]                        [VramOverflowError]
```
