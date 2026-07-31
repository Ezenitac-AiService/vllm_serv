# Quickstart & Validation Guide: Gemma 4 Model Loading Fix

**Feature Branch**: `specs/015-gemma4-model-loading-fix`
**Created**: 2026-07-29

---

## Prerequisites & Setup

1. **Virtual Environment & Dependencies**:
   ```bash
   uv sync
   ```

2. **Gemma 4 MMProj File Verification**:
   - `models/gemma4-2b/gemma-4-E2B_q4_0-it.gguf`
   - `models/gemma4-2b/gemma-4-E2B-it-mmproj.gguf`

---

## Runnable Validation Scenarios

### Scenario 1: Pytest Unit & Integration Test Suite Execution

Run the dual-mode test suite to verify contract enforcement and mock/real mode behaviors:

```bash
uv run pytest tests/unit/test_gemma4_loading.py tests/integration/test_gpu_validation.py -v
```

**Expected Outcome**: All tests pass cleanly (100% pass rate).

---

### Scenario 2: Live GPU Benchmark & Gemma 4 Real Serving Execution

Run the real GPU quality benchmark script across all 6 models including Gemma 4 E2B and E4B:

```bash
uv run python scripts/benchmark_quality.py --auto-download --real
```

**Expected Outcome**:
- `gemma4-e2b` and `gemma4-e4b` load with `36/36 layers offloaded to GPU`.
- Healthcheck returns HTTP 200 OK within 120s.
- 10 evaluation prompts per model completed (100% response rate).
- Benchmark reports generated at `data/reports/analysis_report_quality.md`.
