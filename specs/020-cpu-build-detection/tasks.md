# Tasks: CPU 빌드 감지 및 다중 플랫폼 지원 (llama.cpp)

**Input**: Design documents from `/specs/020-cpu-build-detection/` (`plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/cpu_detector_api.md`, `quickstart.md`)

**Prerequisites**: plan.md (required), spec.md (required)

**Tests**: 헌장 원칙 II (테스트 주도 개발 및 품질 보증)에 따라 모든 사용자 스토리 구현 시 단위/통합 테스트 완성이 필수적입니다.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (`[US1]`, `[US2]`, `[US3]`, `[US4]`)
- Exact file paths included in all task descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 프로젝트 플랫폼 프로필 초기화 및 구성 데이터 정의

- [x] T001 Create target platform profile configuration in `config/platform_profiles.json`
- [x] T002 Update `src/core/config_manager.py` to load and parse `platform_profiles.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: CPU 및 GPU 기능 감지를 위한 핵심 데이터 모델 및 파싱 인프라 구현 (모든 사용자 스토리의 차단 전제조건)

**⚠️ CRITICAL**: 이 단계가 완료되기 전까지 사용자 스토리 작업을 시작할 수 없습니다.

- [x] T003 [P] Define data entities (`CpuFeatureInfo`, `GpuCapabilityInfo`, `LlamaCppBuildFlags`, `TargetPlatformProfile`) in `src/core/cpu_detector.py`
- [x] T004 Implement Linux `/proc/cpuinfo` parsing and CPU flag extraction in `src/core/cpu_detector.py`
- [x] T005 Implement `nvidia-smi` compute capability detection for CUDA architectures in `src/core/cpu_detector.py`

**Checkpoint**: 하드웨어 감지 코어 엔진 준비 완료 - 사용자 스토리 구현 진행 가능

---

## Phase 3: User Story 1 - 레거시 CPU 환경에서 llama.cpp 자동 빌드 (Priority: P1) 🎯 MVP

**Goal**: i7 930(Nehalem, SSE4.2 전용) 레거시 CPU 환경에서 AVX/AVX2/F16C/FMA를 자동으로 비활성화하고 GTX 1070(Compute Capability 6.1) CUDA 호환 플래그를 생성하여 `llama-server` 및 `llama-cpp-python`을 성공적으로 컴파일하고 `Illegal instruction` 크래시 없이 구동

**Independent Test**: `tests/unit/test_cpu_detector.py` 단위 테스트를 통해 AVX 미지원 CPU 파싱 시 `-DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_F16C=OFF -DGGML_FMA=OFF -DCMAKE_CUDA_ARCHITECTURES=61` 플래그 문자열이 올바르게 생성되는지 검증

### Tests for User Story 1 (MANDATORY) ⚠️

- [x] T006 [P] [US1] Create unit tests for legacy CPU (AVX disabled) detection and CMake flag string generation in `tests/unit/test_cpu_detector.py`

### Implementation for User Story 1

- [x] T007 [US1] Implement CMake build argument generator `get_llama_build_flags()` in `src/core/cpu_detector.py` (depends on T003, T004, T005)
- [x] T008 [US1] Integrate `cpu_detector` CMake flags into `verify_and_build_llama_server()` in `src/core/process_manager.py`
- [x] T009 [US1] Integrate `cpu_detector` CMake flags into `setup.sh` for `llama-cpp-python` pip installation
- [x] T010 [US1] Add GPU acceleration fail-fast check (`GpuAccelerationError`) when GPU is missing in `src/core/cpu_detector.py`

**Checkpoint**: User Story 1 완료 - i7 930 레거시 시스템에서 llama.cpp 빌드 및 실행 독립 검증 가능 (MVP 달성)

---

## Phase 4: User Story 2 - 기존 플랫폼과의 빌드 호환성 유지 (Priority: P1)

**Goal**: 최신 CPU(AVX2/FMA 지원) 및 RTX 3060(Compute Capability 8.6) 기존 개발 장비에서 동일한 최적화 플래그를 유지하고 성능 저하가 없음을 검증

**Independent Test**: `tests/unit/test_cpu_detector.py`에서 최신 CPU 파싱 시 `-DGGML_AVX=ON -DGGML_AVX2=ON -DGGML_F16C=ON -DGGML_FMA=ON -DCMAKE_CUDA_ARCHITECTURES=86` 플래그가 정확히 출력되는지 검증

### Tests for User Story 2 (MANDATORY) ⚠️

- [x] T011 [P] [US2] Add unit tests for modern CPU feature detection and RTX 3060 architecture flags in `tests/unit/test_cpu_detector.py`

### Implementation for User Story 2

- [x] T012 [US2] Verify build pipeline backward compatibility and zero performance degradation in `tests/integration/test_build_pipeline.py`

**Checkpoint**: User Story 1과 2가 모두 독자적으로 작동하며, 기존 개발 장비와 레거시 장비 양쪽 지원 완료

---

## Phase 5: User Story 3 - CPU 기능 감지 결과 리포트 (Priority: P2)

**Goal**: 빌드 스크립트 실행 시 감지된 CPU 모델명, 지원 명령어 세트, 최종 선택된 CMake 빌드 플래그를 투명하게 로그 및 CLI로 출력

**Independent Test**: `python -m src.core.cpu_detector --format cmake` 및 `--report` CLI 실행 후 출력 검증

### Tests for User Story 3 (MANDATORY) ⚠️

- [x] T013 [P] [US3] Create CLI contract and report output unit tests in `tests/unit/test_cpu_detector.py`

### Implementation for User Story 3

- [x] T014 [US3] Implement CLI main entry point (`--format cmake`, `--format json`, `--report`) in `src/core/cpu_detector.py`
- [x] T015 [US3] Add human-readable hardware detection log output in `setup.sh` and `src/core/process_manager.py`

**Checkpoint**: 빌드 결과 리포트 기능이 구현되어 운영자가 빌드 플래그 선택 사유를 한눈에 파악 가능

---

## Phase 6: User Story 4 - 타겟 플랫폼 프로필 관리 (Priority: P3)

**Goal**: 신규 타겟 플랫폼 하드웨어 사양(i7 930 + GTX 1070 + 24GB RAM + Ubuntu Server 24.04 LTS)을 플랫폼 프로필 설정으로 관리

**Independent Test**: `ConfigManager().get_platform_profile("legacy-i7-930-gtx1070")` 호출하여 프로필 로딩 확인

### Tests for User Story 4 (MANDATORY) ⚠️

- [x] T016 [P] [US4] Create unit test for platform profile loading and validation in `tests/unit/test_config_manager_profiles.py`

### Implementation for User Story 4

- [x] T017 [US4] Implement `get_platform_profiles()` and profile lookup in `src/core/config_manager.py`

**Checkpoint**: 모든 사용자 스토리 구현 완료

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: 전체 검증 및 문서화 동기화

- [x] T018 [P] Update `quickstart.md` validation commands and documentation
- [x] T019 Execute end-to-end quickstart validation scenarios across `tests/unit/test_cpu_detector.py` and `tests/integration/test_build_pipeline.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 순차 진행 (의존성 없음)
- **Foundational (Phase 2)**: Setup 완료 후 진행 - 모든 사용자 스토리의 차단 전제조건
- **User Stories (Phase 3+)**: Foundational 단계 완료 후 우선순위(P1 → P1 → P2 → P3) 순으로 구현
- **Polish (Phase 7)**: 모든 사용자 스토리 완성 후 실행

### Parallel Opportunities

- **T003**, **T006**, **T011**, **T013**, **T016**, **T018**은 파일이 분리되어 있어 병렬 작업 가능 [P].

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Complete Phase 1 (Setup) & Phase 2 (Foundational)
2. Complete Phase 3 (User Story 1 - 레거시 CPU 빌드 지원)
3. **STOP and VALIDATE**: `pytest tests/unit/test_cpu_detector.py` 실행 및 `Illegal instruction` 방지 검증
4. MVP 완료!

### Incremental Delivery
- MVP (US1: i7 930 레거시 빌드) → US2 (기존 RTX 3060 지원 유지) → US3 (로그 리포트) → US4 (프로필 관리)
