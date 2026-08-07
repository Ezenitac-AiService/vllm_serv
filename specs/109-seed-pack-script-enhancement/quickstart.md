# Quickstart Validation Guide: Seed Pack Script Enhancement

**Feature Identifier**: `109-seed-pack-script-enhancement`  
**Date**: 2026-08-07  

---

## Validation Scenario 1: Standard Seed Pack Generation & Feature 108 Module Verification

Execute seed pack generation script:
```bash
./make_seed_pack.sh
```
**Expected Outcome**:
Generates `dist/vllm_serv_seed.tar.gz` under 15MB and prints green verification logs confirming `gpu_detector.py` and `model_catalog.json` are included.

---

## Validation Scenario 2: `--include-profiles` Flag Verification

Execute seed pack generation script with profile bundling:
```bash
./make_seed_pack.sh --include-profiles -o dist/vllm_serv_seed_with_profiles.tar.gz
```
**Expected Outcome**:
Generates `dist/vllm_serv_seed_with_profiles.tar.gz` and confirms `config/model_context_profiles.json` is packaged in archive verification output.

---

## Validation Scenario 3: Full Shell Scripts Unit Test Execution

Run pytest on shell scripts test suite:
```bash
uv run pytest tests/unit/test_shell_scripts.py
```
**Expected Outcome**: 100% PASS rate.
