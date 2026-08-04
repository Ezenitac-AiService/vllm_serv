# Feature Specification: 3대 멀티 플랫폼 HW 차등 감지 및 훈련 플랫폼(RTX 3060) 최적 하드웨어 가속(3세대 Tensor Cores, TF32, BF16, FlashAttention-2) 자동 설정 (`094-hardware-capability-autodetect`)

**Feature Branch**: `094-hardware-capability-autodetect`

**Created**: 2026-08-04

**Status**: Draft

**Input**: User description: "우리의 세가지 플렛폼 (개발 플렛폼 - e3 gtx 1080ti, 서비스 플렛폼 - i7 930 1070, 훈련 플렛폼 - i7 4770 rtx 3060)에서 마이그레이션 시 - setup.sh 실행시 훈련 플렛폼은 rtx 3060이 지원하는 모든 기능들을 활성화 할수 있도록 인식하고 지원 셋팅을 해야 하지 않을까? 텐서코어 2세대 지원, bf16 지원, flash어텐션2 를 지원하는거 같은데"

## Clarifications

### Session 2026-08-04

- Q: RTX 3060 Ampere sm_86 리서치 결과 명세서(spec.md) 통합 정책 → A: Option A (Ampere sm_86 3세대 Tensor Cores, TF32, BF16, FlashAttention-2 LLAMA_FLASH_ATTN=ON 및 sm_86 전용 C++ NVCC 플래그 명세서 반영)
- Q: 3대 극과 극 병목 플랫폼(CPU 제한 / GPU 제한 / 무제한) 차등 셋팅 명세 반영 정책 → A: Option A (CPU AVX2 유무 및 GPU sm_61/sm_86 자동 탐지 믹스인 명세(FR-006)를 spec.md에 공식 추가 반영)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 훈련 플랫폼(RTX 3060 / Ampere sm_86) 최적 가속 기능 자동 감지 및 셋팅 (Priority: P1) 🎯 MVP

시스템 관리자 및 AI 엔지니어는 훈련 플랫폼(Xeon/i7-4770 + RTX 3060)에서 `./setup.sh` 또는 마이그레이션 파이프라인을 실행할 때, 하드웨어가 RTX 3060(Ampere 아키텍처, Compute Capability 8.6)으로 자동 식별되고, 3세대 Tensor Cores 가속, TF32 / BF16 (bfloat16) 데이터 타입 네이티브 지원, FlashAttention-2 (LLAMA_FLASH_ATTN=ON) 빌드/런타임 옵션이 최적으로 자동 활성화되기를 원한다.

**Why this priority**: 훈련 플랫폼의 Ampere GPU 성능 및 메모리 효율성(3세대 Tensor Cores, TF32/BF16, FlashAttention-2)을 100% 이끌어내어 추론 및 학습 속도를 극대화해야 한다.

**Independent Test**: RTX 3060 플랫폼에서 `setup.sh` 및 `cpu_detector` 구동 시 GPU 프로파일이 `Ampere (sm_86)`로 감지되고, Tensor Cores 3Gen, TF32/BF16, FlashAttention-2 플래그가 자동 활성화되는지 동적 검증 수행.

**Acceptance Scenarios**:

1. **Given** 훈련 플랫폼(RTX 3060) 호스트에서 `./setup.sh`를 실행할 때, **When** 하드웨어 탐지기가 가동되면, **Then** GPU 아키텍처가 `Ampere (sm_86)`로 정확히 식별되고 3세대 Tensor Cores, TF32/BF16, FlashAttention-2 활성화 파라미터가 적용된다.
2. **Given** 셋업이 완료된 후, **When** 서버 및 하드웨어 탐지 리포트를 출력하면, **Then** 하드웨어 가속 프로파일 리포트에 `Tensor Cores 3Gen: ENABLED`, `TF32/BF16 Support: YES`, `FlashAttention-2: ACTIVE`가 명확히 명시된다.

---

### User Story 2 - 3대 멀티 플랫폼(개발/서비스/훈련) 아키텍처 자동 식별 및 차등 셋팅 매핑 (Priority: P2)

운영 관리자는 3가지 상이한 하드웨어 플랫폼 환경(개발: Xeon + GTX 1080Ti Pascal sm_61, 서비스: i7-930 + GTX 1070 Pascal sm_61, 훈련: i7-4770 + RTX 3060 Ampere sm_86)에서 각각 `./setup.sh`를 구동할 때, 각 하드웨어가 지원하는 아키텍처에 맞게 최적의 CUDA C++ 컴파일 파라미터 및 런타임 가속 프로파일이 안전하게 자동 매핑되기를 원한다.

**Independent Test**: 각 플랫폼 환경(Pascal vs Ampere)에서 하드웨어 프로파일 감지기(`cpu_detector`)를 구동할 때 호환되지 않는 미지원 옵션(예: Pascal에서의 FlashAttention-2)을 안전하게 무시하고 플랫폼 전용 최적 설정이 적용되는지 검증.

**Acceptance Scenarios**:

1. **Given** 개발 플랫폼(GTX 1080Ti) 또는 서비스 플랫폼(GTX 1070) 호스트일 때, **When** `./setup.sh`를 가동하면, **Then** Pascal (sm_61) 프로파일이 설정되고 FlashAttention-2 대신 레거시/SDPA CUDA 가속이 적용된다.
2. **Given** 훈련 플랫폼(RTX 3060) 호스트일 때, **When** `./setup.sh`를 가동하면, **Then** Ampere (sm_86) 프로파일이 적용되어 3세대 텐서코어, TF32/BF16, FlashAttention-2의 풀 파워 옵션이 차등 설정된다.

---

## Edge Cases & Error Handling *(mandatory)*

- GPU Compute Capability 탐지 실패 시: Pascal (sm_61) 호환 프로파일로 안전하게 폴백하여 파이프라인 비정상 종료 방지.
- FlashAttention-2 빌드 가용 C++ 헤더/라이브러리 미지원 시스템: log_warn 경고를 출력하고 SDPA (Scaled Dot-Product Attention) 가속 모드로 자동 하향 복구.

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: 3대 플랫폼(개발: GTX 1080Ti, 서비스: GTX 1070, 훈련: RTX 3060) 하드웨어 자동 탐지 및 차등 프로파일 믹스인 구현 완료
- **DoD-002**: RTX 3060 훈련 플랫폼 탐지 시 3세대 Tensor Cores, TF32/BF16, FlashAttention-2 (`LLAMA_FLASH_ATTN=ON`) 자동 연동 파이프라인 수립
- **DoD-003**: 멀티 플랫폼 하드웨어 자동 탐지 및 셋팅 단위/통합 테스트 수트 (`tests/unit/test_hardware_autodetect.py`) 100% 통과 입증

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST `./setup.sh` 및 `src/core/cpu_detector.py` 구동 시 호스트 GPU의 Compute Capability (Pascal sm_61 vs Ampere sm_86 등) 및 GPU 아키텍처명을 정밀 자동 탐지해야 한다.
- **FR-002**: System MUST RTX 3060 (Compute Capability 8.6 이상) 훈련 플랫폼 탐지 시, 3세대 Tensor Cores, TF32 및 BF16 데이터 타입 네이티브 지원 및 FlashAttention-2 (`LLAMA_FLASH_ATTN=ON`) 가속 옵션을 컴파일 및 런타임 셋팅에 자동 반영해야 한다.
- **FR-003**: System MUST 개발 플랫폼(GTX 1080Ti) 및 서비스 플랫폼(GTX 1070) 등 Pascal (sm_61) 아키텍처 탐지 시, 해당 GPU 하드웨어가 미지원하는 옵션을 감안하여 FP16/SDPA 중심의 안정적 가속 셋팅으로 차등 매핑해야 한다.
- **FR-004**: System MUST `scripts/common.sh` 및 `status_server.sh` 리포트에 3대 플랫폼별 탐지된 하드웨어 프로파일 및 최적 가속 셋팅 상태(Tensor Cores 3Gen, TF32/BF16, FlashAttention-2 활성화 여부)를 명확히 출력해야 한다.
- **FR-005**: System MUST 3대 멀티 플랫폼 탐지 및 차등 셋팅 검증을 위한 단위 테스트 수트 (`tests/unit/test_hardware_autodetect.py`)를 수립하고 100% 통과시켜야 한다.
- **FR-006**: System MUST 호스트 CPU의 명령어 세트(AVX2 유무) 및 GPU Compute Capability (`sm_61` vs `sm_86`)를 2원 축으로 탐지하여, CPU 병목 플랫폼(i7-930: `-mavx2` 제외 컴파일 및 VRAM 100% 오프로드), GPU 기능 제한 플랫폼(GTX 1080Ti: FP16/SDPA 적용), 무제한 플랫폼(RTX 3060: 3세대 Tensor Cores/TF32/BF16/FlashAttn2) 3원 차등 컴파일 및 런타임 셋팅을 자동 연동해야 한다.

### Key Entities

- **HardwareProfileCapability**: 플랫폼 하드웨어 특성 엔티티 (`platform_type`, `gpu_name`, `compute_capability`, `tensor_cores_gen`, `supports_tf32`, `supports_bf16`, `supports_flash_attn2`, `active_profile`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: RTX 3060 훈련 플랫폼 탐지 정확도 100% 및 4대 핵심 가속(Tensor Cores 3Gen, TF32, BF16, FlashAttention-2) 셋팅 자동 반영율 100%.
- **SC-002**: 개발/서비스/훈련 3대 하드웨어 플랫폼 차등 프로파일 탐지 및 컴파일 셋팅 호환 성공률 100%.
- **SC-003**: 하드웨어 가속 자동 감지 테스트 수트 통과율 100%.

## Assumptions

- 훈련 플랫폼은 RTX 3060 (Ampere architecture, Compute Capability 8.6) GPU를 탑재하고 있으며, 개발/서비스 플랫폼은 Pascal architecture (Compute Capability 6.1) GPU를 탑재함.
