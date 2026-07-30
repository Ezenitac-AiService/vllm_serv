# Research: Seed Pack Archiver & Migration Pipeline

**Feature Branch**: `specs/019-seed-pack-generator`
**Date**: 2026-07-30

## Research Questions & Decisions

### 1. Packaging Tool & Compression Strategy

- **Decision**: POSIX `tar` (`tar -czf`) as primary compression engine, with `zip` (`zip -r`) as secondary format when `--zip` flag is passed.
- **Rationale**:
  - `tar` and `gzip` are pre-installed across virtually all Linux/POSIX environments without needing external package installation.
  - `tar` natively supports `--exclude` parameters for excluding patterns (`models/*`, `.venv/*`, `.bin/*`, `__pycache__/*`, etc.).
  - `zip` support can be conditionally executed if `zip` binary is present in system PATH, with clear error message if missing.
- **Alternatives Considered**:
  - *Python `tarfile` / `zipfile` script*: Rejected as primary entrypoint to keep `make_seed_pack.sh` runnable directly in lightweight bash environments prior to `uv` / Python virtualenv bootstrap.

---

### 2. Exclusion Pattern & Directory Traversal Rules

- **Decision**: Explicit pattern-based exclusion list passed directly to `tar --exclude`.
- **Exclusion List**:
  - `models/*` (Large GGUF model files)
  - `.venv/*` (Python virtual environment)
  - `.bin/*` (Compiled llama-server C++ binaries)
  - `logs/*` (Runtime log files)
  - `build/*` (CMake build artifacts)
  - `dist/*` (Seed pack output directory)
  - `__pycache__/*`, `*.pyc`, `*.pyo` (Bytecode caches)
  - `.git/*`, `.github/*` (Git metadata)
  - `.pytest_cache/*`, `.coverage`, `htmlcov/*` (Test artifacts)
  - `*.tar.gz`, `*.zip` (Existing archives)
- **Rationale**: Guarantees that the resulting seed pack contains only pure source code and scripts (< 10MB total).

---

### 3. CLI Argument Parsing in Bash

- **Decision**: Custom `while [[ $# -gt 0 ]]` option loop in `scripts/make_seed_pack.sh`.
- **Supported Options**:
  - `-o`, `--output <path>`: Specifies custom archive output file path (Default: `dist/vllm_serv_seed.tar.gz` or `dist/vllm_serv_seed.zip`).
  - `--zip`: Switches archive format from `.tar.gz` to `.zip`.
  - `-h`, `--help`: Prints usage help text.
- **Rationale**: POSIX compliant, simple, readable, and supports long options (`--zip`, `--output`) cleanly without requiring external tools.

---

### 4. Automated Testing & Verification Strategy

- **Decision**: Pytest integration test suite in `tests/unit/test_seed_pack.sh` / `tests/integration/test_seed_pack.py`.
- **Strategy**:
  - Run `make_seed_pack.sh` in a pytest temporary directory (`tmp_path`).
  - Inspect generated `.tar.gz` file using Python's `tarfile` module to assert:
    1. Mandatory files exist (`pyproject.toml`, `setup.sh`, `src/core/process_manager.py`, `config/model_catalog.json`, `README.md`).
    2. Excluded directories do NOT exist (`models/`, `.venv/`, `.bin/`, `__pycache__/`).
    3. File size is under 10MB threshold.
  - Test archive extraction and basic setup script validation.
