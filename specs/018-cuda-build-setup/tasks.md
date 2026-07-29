# Tasks: Automated CUDA-Enabled llama.cpp Build & Setup Pipeline

**Input**: Design documents from `/specs/018-cuda-build-setup/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (`[US1]`, `[US2]`, `[US3]`)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project dependency registration for CUDA-enabled build persistence

- [x] T001 Add `llama-cpp-python[server]>=0.3.0`, `cmake>=3.28`, `ninja>=1.11` to `dependencies` array in `pyproject.toml`
- [x] T002 [P] Verify `uv sync` environment synchronization configuration in `pyproject.toml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core CUDA fail-fast detector helper that blocks user story execution

**⚠️ CRITICAL**: No user story implementation can begin until this phase is complete

- [x] T003 Implement CUDA Toolkit (`/usr/bin/nvcc`) and `nvidia-smi` fail-fast detector helper in `src/core/gpu_detector.py` (FR-005)
- [x] T004 [P] Add unit tests for CUDA detector and `GpuAccelerationError` fail-fast validation in `tests/unit/test_gpu_detector.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - setup.sh 실행 시 CUDA 기반 llama-cpp-python 자동 빌드 및 의존성 동기화 (Priority: P1) 🎯 MVP

**Goal**: Ensure `setup.sh` automatically compiles `llama-cpp-python[server]` with CUDA acceleration flags (`CMAKE_ARGS="-DGGML_CUDA=on"`) and fails fast if CUDA SDK is missing.

**Independent Test**: `uv run python -c "import llama_cpp; assert llama_cpp.llama_supports_gpu()"` returns `True`.

- [x] T005 [P] [US1] Create unit test for CUDA GPU support verification (`llama_supports_gpu()`) in `tests/unit/test_gpu_detector.py`
- [x] T006 [US1] Refactor `scripts/setup.sh` Step 2 to validate `nvcc` presence and fail fast with clear error if CUDA SDK is missing (FR-005)
- [x] T007 [US1] Update `scripts/setup.sh` Step 2 to execute `CMAKE_ARGS="-DGGML_CUDA=on" uv pip install llama-cpp-python[server] --no-binary llama-cpp-python --force-reinstall` (FR-001, FR-002)
- [x] T008 [US1] Add post-install assertion step `uv run python -c "import llama_cpp; assert llama_cpp.llama_supports_gpu()"` in `scripts/setup.sh`

**Checkpoint**: User Story 1 fully functional - `llama_supports_gpu()` returns `True` independently.

---

## Phase 4: User Story 2 - ProcessManager C++ llama-server CMake CUDA 자동 컴파일 보완 (Priority: P2)

**Goal**: Ensure `ProcessManager` passes `-DGGML_CUDA=ON` to CMake when compiling C++ native `llama-server`.

**Independent Test**: `ProcessManager.verify_and_build_llama_server()` builds native CUDA binary `.bin/llama-server`.

- [x] T009 [P] [US2] Create unit test for CMake `-DGGML_CUDA=ON` flag injection in `tests/unit/test_process_manager.py`
- [x] T010 [US2] Refactor `ProcessManager.verify_and_build_llama_server()` in `src/core/process_manager.py` to inject `-DGGML_CUDA=ON` into `cmake -B build` invocation (FR-003)

**Checkpoint**: User Stories 1 AND 2 working independently.

---

## Phase 5: User Story 3 - nvtop & nvidia-smi GPU VRAM 모니터링 무결성 검증 (Priority: P2)

**Goal**: Verify `nvidia-smi` and `nvtop` display active PID and allocated VRAM (>2000MB) when server is in READY status.

**Independent Test**: `./status_server.sh` and `nvidia-smi` report resident VRAM > 2000MB and server process PID.

- [x] T011 [P] [US3] Create integration test for VRAM offload and process PID detection in `tests/integration/test_gpu_validation.py`
- [x] T012 [US3] Update `scripts/status_server.sh` to query and highlight GPU process PID and VRAM usage from `nvidia-smi` (FR-004)

**Checkpoint**: All user stories functional independently and end-to-end.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation updates and end-to-end validation

- [x] T013 [P] Update `README.md` with CUDA build setup instructions and `nvtop` verification guidelines
- [x] T014 Run full test suite `uv run pytest -v` and validate scenarios in `quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories.
- **User Stories (Phases 3-5)**: All depend on Foundational phase completion.
  - Phase 3 (US1, P1) → Phase 4 (US2, P2) → Phase 5 (US3, P2).
- **Polish (Phase 6)**: Depends on all user stories being complete.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) and Phase 2 (Foundational).
2. Complete Phase 3 (User Story 1 - CUDA pip build & setup.sh).
3. **VALIDATE**: Run `uv run python -c "import llama_cpp; assert llama_cpp.llama_supports_gpu()"`.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready.
2. Add US1 → CUDA pip build → Validate MVP.
3. Add US2 → Native CMake CUDA build → Validate.
4. Add US3 → nvtop / nvidia-smi VRAM monitoring → Validate.
5. Run Polish (Phase 6) & Quickstart scenarios.
