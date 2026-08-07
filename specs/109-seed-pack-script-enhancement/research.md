# Technical Research: Seed Pack Script Enhancement

**Feature Identifier**: `109-seed-pack-script-enhancement`  
**Date**: 2026-08-07  

---

## 1. Archive Inclusions & Feature 108 Verification

### Decision
Enhance `scripts/make_seed_pack.sh` archive content verification routine to explicitly assert that `src/core/gpu_detector.py` (containing `read_gguf_metadata_architecture`) and `config/model_catalog.json` (containing GQA architecture metadata) are successfully packaged.

### Rationale
Feature 108 introduced pure-Python GGUF header parsing and GQA KV cache calculations. Without `src/core/gpu_detector.py` and `config/model_catalog.json`, migration targets would fail to compute dynamic context windows.

---

## 2. CLI Option `--include-profiles`

### Decision
Add CLI flag `--include-profiles` to `scripts/make_seed_pack.sh`.
- By default: `config/model_context_profiles.json` remains excluded to ensure lightweight initial state.
- When `--include-profiles` is passed: `INCLUDE_PROFILES=1` removes `config/model_context_profiles.json` from the exclude list and packages existing benchmark profiles for instant reuse.

---

## 3. Backward Compatibility

Maintain exact CLI compatibility for existing flags (`-o/--output`, `--zip`, `--build-legacy`, `--skip-legacy-build`, `--wheel-path`).
