# Data Model: Seed Pack Script Enhancement

**Feature Identifier**: `109-seed-pack-script-enhancement`  
**Date**: 2026-08-07  

---

## Data Entities & Configurations

### 1. `SeedPackCliOptions`
Represents the command line options parsed by `scripts/make_seed_pack.sh`.

- `output_path`: `str` (Default: `dist/vllm_serv_seed.tar.gz` or `dist/vllm_serv_seed.zip`)
- `use_zip`: `bool` (Default: `false`)
- `build_legacy`: `bool` (Default: `true`)
- `include_profiles`: `bool` (Default: `false`, enabled via `--include-profiles`)
- `custom_wheel_path`: `Optional[str]`

---

### 2. `SeedPackArchiveManifest`
Represents the mandatory files verified inside the generated tarball/zip archive.

- `gpu_detector.py`: `bool` (Required)
- `model_catalog.json`: `bool` (Required)
- `sample/common.py`: `bool` (Required)
- `specs/`: `bool` (Required)
- `start_server.sh`: `bool` (Required)
- `ensure_models.py`: `bool` (Required)
- `auxiliary_manager.py`: `bool` (Required)
- `model_context_profiles.json`: `bool` (Conditional on `include_profiles == true`)
