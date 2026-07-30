# Data Model: Seed Pack Archiver & Migration Pipeline

**Feature Branch**: `specs/019-seed-pack-generator`
**Date**: 2026-07-30

## Entities & Data Schemas

### 1. SeedPackArchive (Domain Artifact Entity)

Representing the generated migration archive file.

| Field | Type | Description | Constraints / Validation |
|---|---|---|---|
| `file_name` | `str` | Name of the output archive file | e.g. `vllm_serv_seed.tar.gz` or `vllm_serv_seed.zip` |
| `output_path` | `str` | Absolute/relative file path | Must reside in valid directory (default: `dist/`) |
| `format` | `enum` | Compression format | `tar.gz` or `zip` |
| `size_bytes` | `int` | Total compressed file size in bytes | Must be < 10,485,760 bytes (10MB) |
| `file_count` | `int` | Total archived file count | Positive integer (typically 30~100 files) |

---

### 2. SeedPackGeneratorOptions (CLI Config Entity)

Representing the configuration passed via CLI arguments to `make_seed_pack.sh`.

| Option Flag | Field Name | Type | Default Value | Description |
|---|---|---|---|---|
| `-o`, `--output` | `output_path` | `str` | `"dist/vllm_serv_seed.tar.gz"` | Custom path for generated archive file |
| `--zip` | `use_zip` | `bool` | `False` | When True, generates `.zip` format instead of `.tar.gz` |
| `-h`, `--help` | `show_help` | `bool` | `False` | Prints usage help and exits 0 |

---

### 3. Inclusion / Exclusion Manifest Rules

#### Included Directories & Files (Mandatory Assets)
- `pyproject.toml`
- `README.md`
- `src/` (All source code: `src/api/`, `src/core/`)
- `config/` (Catalog and server configs: `config/model_catalog.json`, `config/server_config.json`)
- `scripts/` (All shell scripts: `setup.sh`, `start_server.sh`, `stop_server.sh`, `status_server.sh`, `make_seed_pack.sh`, `benchmark_quality.py`)
- `tests/` (All unit and integration tests)
- `.specify/` (Specification metadata and templates)

#### Excluded Patterns (Excluded Artifacts)
- `models/*`
- `.venv/*`
- `.bin/*`
- `logs/*`
- `build/*`
- `dist/*`
- `__pycache__/*`
- `*.pyc`, `*.pyo`
- `.git/*`
- `.pytest_cache/*`
- `*.tar.gz`, `*.zip`

---

### 4. SeedPackVerificationReport (Validation Result Entity)

Output entity generated during automated pytest suite validation.

```json
{
  "archive_path": "dist/vllm_serv_seed.tar.gz",
  "format": "tar.gz",
  "size_mb": 0.45,
  "is_under_10mb": true,
  "mandatory_files_present": [
    "pyproject.toml",
    "scripts/setup.sh",
    "src/core/process_manager.py",
    "config/model_catalog.json"
  ],
  "excluded_patterns_verified": [
    "models/",
    ".venv/",
    ".bin/",
    "__pycache__/"
  ],
  "verification_passed": true
}
```
