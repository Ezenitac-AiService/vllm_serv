# Quickstart Validation Guide: 벤치마크 파이프라인 최적 모델 및 컨텍스트 윈도우 동적 선정 검증

**Feature Identifier**: `110-benchmark-model-selection-fix`  
**Date**: 2026-08-07  

---

## 1. Environment & Prerequisites

- Python 3.12 (`uv` virtual environment active)
- CUDA GPU environment (or CPU Fallback test environment)
- Repository root: `/home/dev/storage/vllm_serv`

---

## 2. Validation Scenarios

### Scenario 1: Unit Test Suite Verification
**Goal**: Verify C-B-A hybrid sorting algorithm and schema dereferencing logic via pytest.

```bash
uv run pytest tests/unit/test_benchmark_context.py -k "test_evaluate_all_catalog_models"
```
**Expected Outcome**: 100% Green PASS with dynamic context window assertion.

---

### Scenario 2: End-to-End CLI Verification (`--force-benchmark`)
**Goal**: Run forced benchmark across candidate models and assert dynamic Stage 4 selection.

```bash
uv run python scripts/benchmark_context_window.py --force-benchmark
```
**Expected Outcome**:
- Stage 4 log displays real dynamic `ctx` (e.g. `ctx=16384` or `ctx=20480`), NOT hardcoded `4096`.
- Best model selected is dynamically computed via C-B-A algorithm.
