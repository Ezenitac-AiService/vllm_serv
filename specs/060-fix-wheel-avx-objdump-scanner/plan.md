# Implementation Plan: 060-fix-wheel-avx-objdump-scanner

## Technical Context

- **Feature Directory**: `specs/060-fix-wheel-avx-objdump-scanner`
- **Target Files**:
  - `scripts/verify_wheel_binary.py`
  - `scripts/make_seed_pack.sh`
  - `tests/unit/test_seed_pack.py`
- **Design Artifacts**:
  - `research.md` (Decision 1: `objdump -d` instruction disassembly, Decision 2: SIMD disable flags)
  - `data-model.md` (`WheelVerificationResult` & `LegacyWheelBuildConfig`)
  - `contracts/wheel-verification-contract.json`
  - `quickstart.md`

---

## Constitution Check

- [x] **Principle I (Language Policy)**: All planning documents and user-facing communications are written in Korean.
- [x] **Principle II (Real-Integration TDD)**: Tests in `tests/unit/test_seed_pack.py` are written and run against real binaries with ZERO mocks in production code.
- [x] **Principle IV (Definition of Done)**: Done criteria measured by 100% green pytest execution and `[POST-BUILD SUCCESS]`.
- [x] **Principle VI (uv Environment)**: All commands execute with `uv run`.
- [x] **Principle VII (Mandatory Regression Testing)**: Full unit regression suite `uv run pytest tests/unit/test_seed_pack.py` passes 100%.

---

## Proposed Changes

### Component 1: `scripts/verify_wheel_binary.py`
- Update `scan_so_with_python_bytes()` to use `objdump -d --no-show-raw-insn` instruction-level disassembly.
- Match mnemonics with `^\s*[0-9a-f]+:\s+(v[a-z0-9]+)\b` (excluding `verr`, `verw`, `vmread`, `vmwrite`, `vmmcall`, `vptr`).
- Retain pure Python fallback parsing ELF `SHF_EXECINSTR` headers with 3-byte VEX map select bit validation.

### Component 2: `scripts/make_seed_pack.sh`
- Update `SKBUILD_CMAKE_ARGS` and `CMAKE_ARGS` to include `-DGGML_CUDA=ON -DGGML_NATIVE=OFF -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_AVX512=OFF -DGGML_AVX512_VBMI=OFF -DGGML_AVX512_VNNI=OFF -DGGML_AVX512_BF16=OFF -DGGML_AVX_VNNI=OFF -DGGML_F16C=OFF -DGGML_FMA=OFF -DGGML_BMI2=OFF -DCMAKE_CUDA_ARCHITECTURES=61 -DCMAKE_C_FLAGS=-march=x86-64 -DCMAKE_CXX_FLAGS=-march=x86-64`.

### Component 3: `tests/unit/test_seed_pack.py`
- Add unit assertions for `objdump` disassembly scanner and SIMD disable flags.

---

## Verification Plan

### Automated Tests
```bash
uv run pytest tests/unit/test_seed_pack.py
```

### Manual Verification
```bash
./scripts/make_seed_pack.sh --build-legacy
uv run python scripts/verify_wheel_binary.py wheels/legacy_i7_930/llama_cpp_python-*.whl
```
