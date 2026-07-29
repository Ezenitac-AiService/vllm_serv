# Feature Specification: GPU/CUDA 하드웨어 가속 인식, VRAM 로드 검증 및 예외 처리 (GPU CUDA Acceleration & VRAM Load Validation)

**Feature Branch**: `010-gpu-cuda-vram-validation`

**Created**: 2026-07-29

**Status**: Draft

**Input**: User description: "llama 바이너리가 cpu 전용이라는게 말이 되? 구현된 프로젝트에서, gpu 인식과 cuda 가속, 모델이 vram에 로드 되었는지 확인하고 예외처리하는 부분이 없어? 설마 전부 목업이었던거야?"

## Clarifications

### Session 2026-07-29

- Q: 기존 코드베이스 내 목업/더미 로직 및 미사용 회피 코드 정제 범위 → A: 코어 모듈(`src/core/`), 평가 모듈(`src/eval/`), 벤치마크 스크립트(`scripts/`) 전반의 하드코딩된 목업 응답, 더미 데이터, 미사용 임포트를 전수 조사하여 100% 실제 GPU/CUDA 런타임 실측 및 예외 처리 로직으로 전환 및 리팩토링합니다.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - GPU/CUDA 하드웨어 가속 사전 검증 및 자동 감지 (Priority: P1) 🎯 MVP

시스템 엔지니어 및 테스터는 서빙 프로세스 개설 시 시스템에 NVIDIA GPU 및 CUDA 환경(드라이버, CUDA 백엔드)이 정상적으로 사용 가능한지 자동으로 사전 검증하고, CPU 전용 실행 바이너리가 감지되거나 GPU 사용 불가 환경인 경우 이를 즉각 경고 및 차단할 수 있어야 합니다.

**Why this priority**: CPU 전용 바이너리로 인해 서빙 성능이 저하되는 무의미한 추론 실행을 방지하고 GPU 100% 가속 환경을 보장하기 위함입니다.

**Independent Test**: CUDA 디바이스 사용 불가능 상태 또는 CPU-only 바이너리 실행 시 사전 헬스체크 단에서 경고 예외를 발생시키고 안전 종료되는지 검증 가능합니다.

**Acceptance Scenarios**:

1. **Given** NVIDIA GPU 및 CUDA 환경이 정상 구동 중일 때, **When** 서빙 서버가 구동되면, **Then** GPU 하드웨어 디바이스(GTX 1080 Ti) 및 CUDA 백엔드가 100% 정상 감지되어 프로세스가 개설됩니다.
2. **Given** 실행 바이너리가 CPU-only 전용 바이너리(CUDA 미지원)이거나 CUDA 백엔드 로드에 실패할 경우, **When** 프로세스 구동 시도 시, **Then** `CPU_FALLBACK_WARNING` 에러 메시지와 함께 서빙 개설이 즉시 안전 차단됩니다.

---

### User Story 2 - VRAM 100% 레이어 오프로딩 및 실시간 로드 검증 (Priority: P2)

사용자는 모델 로드 시 모델 가중치 전체 레이어 및 CLIP 멀티모달 가중치가 GPU VRAM에 100% 오프로드되었음을 실시간 로그 및 프로세스 상태로 명확히 검증받을 수 있어야 합니다.

**Why this priority**: 일부 레이어만 CPU RAM으로 튕겨나가거나 혼용되어 추론 성능 병목이 발생하는 현상을 완벽히 통제하기 위함입니다.

**Independent Test**: 서빙 프로세스 로딩 시 로그/API 상태를 통해 전체 레이어 및 CLIP 프로젝터의 VRAM 오프로드 완료 비율(100%)을 검증할 수 있습니다.

**Acceptance Scenarios**:

1. **Given** GGUF 모델 서빙 개설 시, **When** 프로세스 런타임 로그가 수집되면, **Then** `n_gpu_layers`에 의해 100% 레이어가 VRAM에 탑재되었음이 검증되고 `ServerProcessState`에 `vram_offloaded=True`로 기록됩니다.
2. **Given** VRAM 용량이 부족하여 일부 레이어가 RAM으로 강제 롤백되는 경우, **When** 검증 로직이 동작하면, **Then** `VRAM_PARTIAL_OFFLOAD_ERROR` 예외가 발생하며 명확한 VRAM 부족 메시지를 반환합니다.

---

### User Story 3 - VRAM 해제 무결성 및 OOM 사전 차단 예외 처리 (Priority: P3)

사용자는 모델 스위칭 시 이전 모델의 GPU VRAM 점유가 0MB로 완전히 반납되었는지 검증 후 신규 모델을 로드하여 CUDA OOM(Out of Memory) 크래시를 예방할 수 있어야 합니다.

**Why this priority**: 연속된 모델 동적 스위칭 과정에서 잔여 VRAM 누수로 인한 GPU 렌더링/추론 중단 현상을 방지하기 위함입니다.

**Acceptance Scenarios**:

1. **Given** 구동 중인 서빙 프로세스 언로드 요청 시, **When** `stop_process`가 완료되면, **Then** GPU Memory-Usage가 0MiB(기초 점유 제외)로 클리어되었음이 검증된 후 신규 모델 개설이 진행됩니다.

---

### Edge Cases

- **CUDA 드라이버 런타임 불일치**: CUDA 런타임 버전을 찾을 수 없거나 nvcc 비활성화 시 명확한 문제 해결 안내 메시지 출력.
- **VRAM 실시간 오버플로우**: 추론 컨텍스트 확장 시 VRAM 한계 초과 시 OOM 차단 예외 처리.

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: GPU/CUDA 하드웨어 검증기 모듈(`src/core/gpu_detector.py`) 구현 완료 및 단위 테스트 통과.
- **DoD-002**: `ProcessManager` 내 CUDA 백엔드 로드 및 VRAM 100% 오프로드 실시간 검증 예외 처리 구현.
- **DoD-003**: CPU 전용 차단, VRAM 실시간 검증에 대한 전체 pytest 케이스 작성 및 100% 통과.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 시스템은 프로세스 개설 전 GPU 존재 여부 및 CUDA 가속 지원 백엔드 탑재 여부를 자동 검증해야 합니다.
- **FR-002**: 시스템은 CPU 전용 바이너리 실행 시 서빙 프로세스 개설을 차단하고 `GpuAccelerationError` 예외를 발생시켜야 합니다.
- **FR-003**: 시스템은 모델 로드 시 전체 트랜스포머 레이어 및 CLIP 멀티모달 가중치가 GPU VRAM에 100% 오프로드되었는지 검증해야 합니다.
- **FR-004**: 시스템은 모델 스위칭 시 이전 모델의 VRAM 점유가 완전히 반납되었는지 검증한 후 다음 프로세스를 개설해야 합니다.
- **FR-005**: 벤치마크 파이프라인 및 서빙 서버 API는 GPU 검증 결과 및 VRAM 오프로드 상태를 응답 메타데이터에 포함해야 합니다.
- **FR-006**: 시스템은 코어 모듈(`src/core/`), 평가 모듈(`src/eval/`), 벤치마크 스크립트(`scripts/`) 내 하드코딩된 목업/더미 응답 및 미사용 임포트를 전수 정제하고 100% 실제 GPU/CUDA 런타임 추론 및 헬스체크 로직을 수행해야 합니다.
- **FR-007**: 서빙 런타임 실패 발생 시 목업 데이터로 회피(fallback)하지 않고, 명시적 GPU/VRAM 예외(`GpuAccelerationError`, `VramOverflowError`)를 던져 시스템 상태에 정확히 반영해야 합니다.

### Key Entities

- **GpuDeviceInfo**: device_id, name, total_vram_mb, free_vram_mb, cuda_version, is_cuda_available
- **VramOffloadStatus**: model_id, total_layers, offloaded_layers, is_fully_offloaded, offloaded_vram_mb

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: CPU 전용 실행 시도가 100% 사전 감지 및 차단되어 잘못된 추론 구동을 방지해야 합니다.
- **SC-002**: VRAM 100% 오프로드 검증을 통해 GPU 추론 속도(TPOT)가 30 tok/s 이상 달성되어야 합니다.
- **SC-003**: 신규 및 기존 pytest 테스트 수트 100% 통과율을 유지해야 합니다.

## Assumptions

- 환경 내 NVIDIA GPU(GTX 1080 Ti 11GB) 및 nvidia-smi / CUDA 드라이버 환경이 구축되어 있다고 가정합니다.
- `huggingface_hub` 및 `llama-server` CUDA 실행 가능 환경을 전제로 합니다.
