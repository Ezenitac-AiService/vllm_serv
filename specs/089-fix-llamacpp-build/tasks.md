# Tasks: llama.cpp 빌드 검증 및 휠 컴파일 파이프라인 수정 (fix-llamacpp-build)

**Input**: Design documents from `specs/089-fix-llamacpp-build/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/cuda_build_api.json, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and task tracking setup

- [x] T001 Initialize feature tasks tracking structure in `specs/089-fix-llamacpp-build/tasks.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure for GPU detection and wheel binary scanning

- [x] T002 [P] Implement `CudaEnvironmentInfo` version detector in `src/core/gpu_detector.py` to parse NVIDIA Driver, CUDA Toolkit (`nvcc`), and cuDNN versions
- [x] T003 [P] Implement `WheelValidationResult` binary scanner in `scripts/verify_wheel_binary.py` to test `llama_supports_gpu_offload()` and inspect ELF `.so` AVX instructions

---

## Phase 3: User Story 1 - GPU 가속 기반 llama.cpp 휠 검증 및 자동 컴파일 (Priority: P1) 🎯 MVP

**Goal**: Validate CUDA GPU offloading (`llama_supports_gpu_offload() == True`) and perform automatic C++ source compilation with `--no-cache-dir` on failure.

**Independent Test**: Run `uv run python scripts/verify_wheel_binary.py --check-live` to verify GPU offload capability and test automatic re-compilation in `scripts/setup.sh`.

- [x] T004 [P] [US1] Add `--check-live` mode to `scripts/verify_wheel_binary.py` for live `.venv` GPU offload verification
- [x] T005 [US1] Update `scripts/setup.sh` Tier 4 build pipeline to execute `uv pip install --no-cache-dir "llama-cpp-python[server]"` when uv cache wheel is CPU-only
- [x] T006 [US1] Integrate `llama_supports_gpu_offload()` fail-fast verification check in `scripts/setup.sh` and `src/core/llama_manager.py`

---

## Phase 4: User Story 2 - 하드웨어 SIMD 및 Compute Capability 동적 매칭 (Priority: P2)

**Goal**: Detect host CPU SIMD capabilities and GPU Compute Capability (e.g. `sm_86`) and construct custom `CMAKE_ARGS`.

**Independent Test**: Execute `python3 -m src.core.cpu_detector --format cmake` and verify output matches target GPU/CPU.

- [x] T007 [P] [US2] Update `src/core/cpu_detector.py` to detect CPU SIMD flags (AVX, AVX2, FMA, F16C) and GPU Compute Capability
- [x] T008 [US2] Integrate dynamic `CMAKE_ARGS` generation into `scripts/setup.sh` based on matched target platform profile

---

## Phase 5: User Story 3 - 4단계 휠 복원 및 결함 자동 복구 파이프라인 (Priority: P3)

**Goal**: Tier 1~4 deterministic wheel restoration with atomic cleanup (uninstall) on build error or interrupt signal.

**Independent Test**: Intercept compilation with SIGINT/SIGTERM and verify corrupted `llama-cpp-python` is uninstalled cleanly.

- [x] T009 [US3] Add signal trap handlers (`trap 'uv pip uninstall -y llama-cpp-python' ERR INT TERM`) in `scripts/setup.sh` to ensure clean environment on build interruption
- [x] T010 [P] [US3] Implement Tier 1~3 prebuilt wheel fast-track restoration logic in `scripts/setup.sh`

---

## Phase 6: User Story 4 - NVIDIA 드라이버 및 CUDA Toolkit 자동 업데이트 스크립트 (Priority: P2)

**Goal**: Create `scripts/update_cuda_drivers.sh` and integrate inline interactive update prompt into `scripts/setup.sh`.

**Independent Test**: Run `sudo ./scripts/update_cuda_drivers.sh` and test `setup.sh` interactive TTY prompt when CUDA/Driver version is outdated.

- [x] T011 [P] [US4] Create `scripts/update_cuda_drivers.sh` helper script for OS package manager (apt/dnf) NVIDIA driver, CUDA toolkit, and cuDNN updates
- [x] T012 [US4] Update `scripts/setup.sh` to detect outdated Driver (<525) or CUDA (<12.0) and prompt user for inline update in interactive TTY mode
- [x] T013 [US4] Add non-interactive (CI/CD) fail-fast branch in `scripts/setup.sh` with manual update command output

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and end-to-end status reporting

- [x] T014 [P] Update `scripts/status_server.sh` report to output CUDA Toolkit (`nvcc`), GPU Driver, cuDNN, and `llama_supports_gpu_offload()` status
- [x] T015 Run end-to-end verification against `specs/089-fix-llamacpp-build/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1): MVP priority
  - User Story 2 (P2) & User Story 4 (P2): Can run after US1 or in parallel
  - User Story 3 (P3): Enhances build robustness
- **Polish (Phase 7)**: Depends on completion of user stories

### Parallel Opportunities

- `T002` (`gpu_detector.py`) and `T003` (`verify_wheel_binary.py`) can run in parallel in Phase 2
- `T004` (`verify_wheel_binary.py`) and `T007` (`cpu_detector.py`) can run in parallel
- `T011` (`update_cuda_drivers.sh`) can run in parallel with US1/US2 implementation
