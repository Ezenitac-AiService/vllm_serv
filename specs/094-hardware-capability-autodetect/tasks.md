# Tasks: 3대 멀티 플랫폼 HW 차등 감지 및 훈련 플랫폼(RTX 3060) 최적 하드웨어 가속 자동 설정 (`094-hardware-capability-autodetect`)

**Input**: Design documents from `/specs/094-hardware-capability-autodetect/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/hardware_autodetect_contract.json, quickstart.md

**Tests**: 프로젝트 헌장(Constitution II, VII)에 따라 모든 과제는 `uv run pytest` 기반의 실측 및 mock 검증을 거칩니다.

**Organization**: 각 User Story별로 태스크가 분류되어 있어 독립적인 구현 및 검증이 가능합니다.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 병렬 수행 가능 (다른 파일, 의존성 없음)
- **[Story]**: 해당 태스크가 속한 사용자 시나리오 (예: US1, US2, US3)
- 명확한 파일 상대/절대 경로가 명시되어 있습니다.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 아키텍처 계약 및 멀티 플랫폼 셋팅 인벤토리 준비

- [X] T001 `specs/094-hardware-capability-autodetect/contracts/hardware_autodetect_contract.json` 계약 스키마 검증

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 3대 플랫폼 2원 축(CPU AVX2 x GPU Compute Capability) 탐지 모듈 구현

**⚠️ CRITICAL**: 이 단계가 완료되기 전에는 User Story 작업을 시작할 수 없습니다.

- [X] T002 [P] `src/core/cpu_detector.py`에 `HardwareProfileCapability` 엔티티 및 CPU AVX2 / GPU Compute Capability (`sm_61` vs `sm_86`) 2원 축 스캐너 연동 (FR-001, FR-006)
- [X] T003 [P] `scripts/common.sh`에 하드웨어 탐지 및 맞춤형 C++ CMAKE_ARGS 산출 믹스인(`detect_hardware_profile`, `get_hardware_cmake_args`) 구현 (FR-004, FR-006)

**Checkpoint**: 하드웨어 탐지 기반 믹스인 수립 완료 - User Story 작업 시작 가능

---

## Phase 3: User Story 1 - 훈련 플랫폼(RTX 3060 / Ampere sm_86) 최적 가속 기능 자동 감지 및 셋팅 (Priority: P1) 🎯 MVP

**Goal**: RTX 3060 (Compute Capability 8.6) 탐지 시 3세대 Tensor Cores, TF32/BF16 네이티브 지원 및 FlashAttention-2 (`LLAMA_FLASH_ATTN=ON`) 자동 연동

**Independent Test**: RTX 3060 mock 환경 테스트 시 Ampere `sm_86`, BF16, FlashAttention-2 플래그가 100% 활성화되는지 검증

### Tests for User Story 1

- [X] T004 [P] [US1] 멀티 플랫폼 탐지 단위 테스트 수트 구현 (`tests/unit/test_hardware_autodetect.py`)

### Implementation for User Story 1

- [X] T005 [P] [US1] `scripts/setup.sh` llama-cpp-python C++ 컴파일 연동 시 Ampere `sm_86` 전용 `LLAMA_FLASH_ATTN=ON` 및 최적 빌드 파라미터 적용 (FR-002)

**Checkpoint**: User Story 1 (훈련 플랫폼 RTX 3060 풀 가속) 연동 완료

---

## Phase 4: User Story 2 - 3대 멀티 플랫폼(개발/서비스/훈련) 아키텍처 자동 식별 및 차등 셋팅 매핑 (Priority: P2)

**Goal**: CPU 병목 (Nehalem i7-930: `-mavx2` 제외 컴파일), GPU 기능 제한 (GTX 1080Ti: FP16/SDPA 적용), 무제한 (RTX 3060: 풀 파워) 3원 차등 매핑 구현

**Independent Test**: Nehalem i7-930 탐지 시 AVX2 플래그 미포함, GTX 1080Ti 탐지 시 SDPA 적용, RTX 3060 탐지 시 FlashAttn2 연동 확인

### Implementation for User Story 2

- [X] T006 [P] [US2] `src/core/cpu_detector.py`에 3대 플랫폼별 (i7-930, GTX 1080Ti, RTX 3060) 하드웨어 특성 리포트 및 파라미터 반환 모듈 추가 (FR-003, FR-006)
- [X] T007 [P] [US2] `scripts/status_server.sh` 및 `scripts/common.sh`에 하드웨어 프로파일 3원 가속 상태 출력 믹스인 연동 (FR-004)
- [X] T008 [US2] `tests/unit/test_hardware_autodetect.py`에서 3대 플랫폼 mock 구동 검증 통과 (T004, T006, T007에 의존)

**Checkpoint**: User Story 1 & 2 3대 플랫폼 극과 극 차등 셋팅 완비

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: 최종 문서화 및 DoD 검증 수행

- [X] T009 [P] `specs/094-hardware-capability-autodetect/quickstart.md` 검증 가이드 문서 업데이트
- [X] T010 [Quickstart 실측] Quickstart 검증 시나리오 1~3단계 전체 수행 및 DoD(DoD-001~003) 달성 최종 확인

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 즉시 시작 가능
- **Foundational (Phase 2)**: Setup 완료 후 실행
- **User Stories (Phase 3+)**: Foundational 완료 후 시작 (US1 → US2)
- **Polish (Phase 5)**: 모든 User Story 완료 후 실행

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 & 2 완료 (2원 축 스캐너 & 믹스인)
2. Phase 3 (User Story 1): RTX 3060 Ampere 풀 가속 및 `test_hardware_autodetect.py` 구현
3. MVP 검증 완료 후 Phase 4 진행
