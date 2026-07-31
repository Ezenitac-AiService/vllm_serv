# Tasks: 060-fix-wheel-avx-objdump-scanner

**Input**: Design documents from `specs/060-fix-wheel-avx-objdump-scanner/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Exact file paths included in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Workspace environment verification and context alignment

- [x] T001 Verify active feature configuration in `.specify/feature.json` and ensure workspace clean state

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared utilities for binary inspection and subprocess disassembler execution

- [x] T002 Verify `objdump` system binary availability and subprocess execution wrapper in `scripts/verify_wheel_binary.py`

---

## Phase 3: User Story 1 - `objdump -d` 어셈블리 디스어셈블러 정밀 스캐너 전환 (Priority: P1) 🎯 MVP

**Goal**: Eliminate false positive byte matches (`0xC4`/`0xC5`) by disassembling shared libraries with `objdump -d` and parsing machine instruction mnemonics.

**Independent Test**: `uv run python scripts/verify_wheel_binary.py wheels/legacy_i7_930/llama_cpp_python-*.whl` returns Exit Code 0 with `avx_clean=True` and `total_avx=0`.

### Tests for User Story 1

- [x] T003 [P] [US1] Add unit test assertions for `objdump` disassembly scanner in `tests/unit/test_seed_pack.py`

### Implementation for User Story 1

- [x] T004 [US1] Update `scan_so_with_python_bytes()` in `scripts/verify_wheel_binary.py` to run `objdump -d --no-show-raw-insn` and regex scan `^\s*[0-9a-f]+:\s+(v[a-z0-9]+)\b` (excluding system instructions `verr`, `verw`, `vmread`, `vmwrite`, `vmmcall`, `vptr`)
- [x] T005 [US1] Add pure Python fallback ELF section header `SHF_EXECINSTR` parsing with 3-byte VEX map select validation `(byte1 & 0x1F) in (1, 2, 3)` in `scripts/verify_wheel_binary.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - `make_seed_pack.sh` C/C++ SIMD 차단 옵션 완결 보강 (Priority: P2)

**Goal**: Ensure `make_seed_pack.sh` passes complete SIMD disable flags to `scikit-build-core` and CMake.

**Independent Test**: `./scripts/make_seed_pack.sh --build-legacy` completes with `[POST-BUILD SUCCESS]`.

### Tests for User Story 2

- [x] T006 [P] [US2] Add unit test assertion `test_make_seed_pack_skbuild_cmake_args` checking `CXXFLAGS=-march=x86-64` in `tests/unit/test_seed_pack.py`

### Implementation for User Story 2

- [x] T007 [US2] Update `SKBUILD_CMAKE_ARGS` and `CMAKE_ARGS` in `scripts/make_seed_pack.sh` to include `-DGGML_CUDA=ON -DGGML_NATIVE=OFF -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_AVX512=OFF -DGGML_AVX512_VBMI=OFF -DGGML_AVX512_VNNI=OFF -DGGML_AVX512_BF16=OFF -DGGML_AVX_VNNI=OFF -DGGML_F16C=OFF -DGGML_FMA=OFF -DGGML_BMI2=OFF -DCMAKE_CUDA_ARCHITECTURES=61 -DCMAKE_C_FLAGS=-march=x86-64 -DCMAKE_CXX_FLAGS=-march=x86-64`

**Checkpoint**: User Story 1 and User Story 2 are fully integrated.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Validation and full suite regression testing

- [x] T008 [P] Execute full unit regression test suite `uv run pytest tests/unit/test_seed_pack.py`
- [x] T009 Execute end-to-end quickstart scenario `./scripts/make_seed_pack.sh --build-legacy` and verify archive creation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Setup.
- **User Story 1 (Phase 3 - MVP)**: Depends on Phase 2.
- **User Story 2 (Phase 4)**: Depends on Phase 3.
- **Polish (Phase 5)**: Depends on Phase 4.

### Parallel Opportunities

- T003 [P] and T006 [P] can run in parallel with foundational preparation.
- T008 [P] can run in parallel during final verification.
