# Tasks: GPU/CUDA 하드웨어 가속 인식, VRAM 로드 검증 및 예외 처리 (GPU CUDA Acceleration & VRAM Load Validation)

**Input**: Design documents from `/specs/010-gpu-cuda-vram-validation/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Project root: `/home/dev/storage/vllm_serv/`
- Core modules: `src/core/`
- Evaluation modules: `src/eval/`
- Scripts: `scripts/`
- Tests: `tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Define GPU device info, VRAM offload status Pydantic models, and custom exception hierarchy

- [x] T001 Define `GpuDeviceInfo`, `VramOffloadStatus` models and `GpuAccelerationError`, `VramOverflowError` exception classes in `src/core/gpu_detector.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement NVIDIA GPU and CUDA backend detector and CPU fallback guards

- [x] T002 Implement NVIDIA GPU and CUDA backend detection engine (`check_gpu_availability`) (FR-001) in `src/core/gpu_detector.py`
- [x] T003 Implement CPU fallback detection and exception throwing in `src/core/process_manager.py`

---

## Phase 3: User Story 1 - GPU/CUDA 하드웨어 가속 사전 검증 및 자동 감지 (Priority: P1) 🎯 MVP

**Goal**: 서빙 프로세스 개설 시 NVIDIA GPU 및 CUDA 환경을 사전 검증하고 CPU 전용 바이너리 시도 시 사전 차단.

**Independent Test**: CUDA 미지원 상태 또는 CPU-only 바이너리 실행 시 사전 단에서 `GpuAccelerationError` 예외를 발생시키고 서빙 개설을 즉시 안전 차단하는지 검증.

### Implementation for User Story 1

- [x] T004 [P] [US1] Add unit tests for GPU detector and CUDA backend checks in `tests/unit/test_gpu_detector.py`
- [x] T005 [US1] Integrate `GpuDetector` into `ProcessManager.spawn_process` to block CPU-only binaries (FR-001, FR-002) in `src/core/process_manager.py`

**Checkpoint**: User Story 1 complete - GPU/CUDA detector and CPU fallback guard verified.

---

## Phase 4: User Story 2 - VRAM 100% 레이어 오프로딩 및 실시간 로드 검증 (Priority: P2)

**Goal**: 모델 로드 시 전체 레이어 및 CLIP 가중치가 GPU VRAM에 100% 오프로드되었는지 실시간 파싱 및 검증.

**Independent Test**: 프로세스 로딩 로그를 파싱하여 전체 레이어 VRAM 오프로드 실패 시 `VramOverflowError`가 발생하는지 검증.

### Implementation for User Story 2

- [x] T006 [P] [US2] Implement real-time stdout/stderr log parsing for 100% VRAM layer offloading (FR-003) in `src/core/process_manager.py`
- [x] T007 [US2] Expose GPU info and VRAM offload status in `LlamaManager` status broadcasting and API (FR-005) in `src/core/llama_manager.py`

**Checkpoint**: User Story 2 complete - Real-time 100% VRAM offload verification verified.

---

## Phase 5: User Story 3 - VRAM 해제 무결성 및 OOM 사전 차단 예외 처리 (Priority: P3)

**Goal**: 모델 스위칭 시 이전 모델의 GPU VRAM 점유 0MB 반납 검증 및 OOM 예방.

**Independent Test**: 모델 언로드 시 VRAM 점유가 정상 해제되었는지 파싱하여 검증.

### Implementation for User Story 3

- [x] T008 [P] [US3] Implement VRAM memory release verification after process termination (FR-004) in `src/core/process_manager.py`
- [x] T009 [US3] Add integration tests for CPU fallback blocking and VRAM offload validation in `tests/integration/test_gpu_validation.py`

**Checkpoint**: User Story 3 complete - VRAM release integrity and integration test suite verified.

---

## Phase 6: Polish & Codebase-wide Mock Refactoring

**Purpose**: Audit and remove all hardcoded mock responses, fake profiling fallbacks, and unused imports across the codebase

- [x] T010 [P] Audit and remove hardcoded mock responses, fallback sample data, and unused imports across `src/core/`, `src/eval/`, and `scripts/benchmark_quality.py` per FR-006, FR-007
- [x] T011 Execute full pytest regression test suite (`uv run pytest`) and validate `specs/010-gpu-cuda-vram-validation/quickstart.md` scenarios

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on US1 completion
- **User Story 3 (Phase 5)**: Depends on US1 & US2 completion
- **Polish (Phase 6)**: Depends on all user stories completion

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & Phase 2 (Pydantic models, GPU detector engine, CPU fallback guards)
2. Complete Phase 3 (User Story 1: GPU/CUDA detector integration & unit tests)
3. **STOP and VALIDATE**: Verify GPU detector functionality via pytest

### Incremental Delivery

1. Setup + Foundational -> GPU Detector & Exception Core Ready
2. User Story 1 -> Automatic GPU/CUDA Detection & CPU Fallback Guard (MVP)
3. User Story 2 -> Real-time 100% VRAM Layer Offload Verification
4. User Story 3 -> VRAM Release Integrity & Integration Tests
5. Polish -> Codebase-wide mock removal & 100% pytest regression pass

---

## Phase 7: Convergence

- [x] T012 Implement real-time stdout/stderr log parsing for 100% VRAM layer offload and raise VramOverflowError on partial RAM fallback per FR-003, US2/AC1, US2/AC2 (missing) in `src/core/process_manager.py`
- [x] T013 Implement VRAM memory release check via nvidia-smi during model unload per FR-004, US3/AC1 (partial) in `src/core/process_manager.py`
- [x] T014 Incorporate real GpuDeviceInfo and VramOffloadStatus models into LlamaManager status broadcasting per FR-005, US2/AC1 (partial) in `src/core/llama_manager.py`

## Phase 8: Convergence

- [x] T015 Integrate real-time VRAM offload log parsing into `LlamaManager._monitor_process()` by calling `ProcessManager.parse_vram_offload_log` on each stdout line and `ProcessManager.verify_vram_offload` when layer data is captured, raising `VramOverflowError` on partial offload per FR-003, US2/AC1, US2/AC2 (missing) in `src/core/llama_manager.py`
- [x] T016 Add GPU detection result and VRAM offload status fields to benchmark report output metadata in `scripts/benchmark_quality.py` per FR-005 (partial)
- [x] T017 Remove hardcoded `fallback_response` mock data from `MODELS_CATALOG` in `scripts/benchmark_quality.py` and raise explicit `GpuAccelerationError` or log skip-with-warning when live inference is unavailable instead of silently using mock data per FR-006, FR-007 (partial)
- [x] T018 Replace hardcoded `cuda_version="13.0"` in `check_gpu_availability()` with dynamic CUDA version detection from nvidia-smi `--query-gpu=cuda_version` output per FR-006 (partial) in `src/core/gpu_detector.py`
- [x] T019 Add `vram_offloaded: Optional[bool]` field to `ProcessState` model and set it to `True` during successful VRAM offload verification per US2/AC1 (partial) in `src/core/process_manager.py`
- [x] T020 Add CUDA driver/runtime version mismatch detection with actionable troubleshooting message in `check_gpu_availability()` per Edge Case: CUDA 드라이버 런타임 불일치 (partial) in `src/core/gpu_detector.py`
- [x] T021 Add runtime VRAM overflow monitoring hook during active inference context expansion to raise `VramOverflowError` on OOM risk per Edge Case: VRAM 실시간 오버플로우 (partial) in `src/core/process_manager.py`

