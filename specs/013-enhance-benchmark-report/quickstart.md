# Quickstart Validation Guide: 6-Model Benchmark Report & Qualitative Answer Comparison

**Feature Directory**: `specs/013-enhance-benchmark-report`  
**Created Date**: 2026-07-29  

---

## Runnable Validation Scenarios

### Scenario 1: Execute Full 6-Model Real GPU Benchmark & Verify Report Output
Verify that all 6 models are listed in the comparison table with zero omitted rows, qualitative sample comparisons, context scaling metrics, and 5-persona deep analysis sections.

```bash
uv run python scripts/benchmark_quality.py --auto-download --real
```

**Expected Outcomes**:
1. Console outputs `[1/6] Gemma 4 E2B` through `[6/6] Qwen 3.5 9B`.
2. Output report file generated at [`specs/013-enhance-benchmark-report/analysis_report_quality.md`](file:///home/dev/storage/vllm_serv/specs/013-enhance-benchmark-report/analysis_report_quality.md) and [`data/reports/analysis_report_quality.md`](file:///home/dev/storage/vllm_serv/data/reports/analysis_report_quality.md).
3. The Markdown table in `Section 2` contains exactly 6 model rows (`gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`, `qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b`).
4. `Section 3` contains `<details><summary>` collapsible text diff blocks comparing Golden Ground Truth vs Model Output.
5. `Section 4` contains the Context Window Capacity & Scaling Limits table (`n_ctx`: 4K, 8K, 16K, 32K).
6. `Section 5` contains the 5-Persona Deep Analysis Report (Data Analyst, DL Expert, Fine-Tuning Expert, DevOps Manager, AI Architect).

### Scenario 2: Run Full Pytest Suite for Report Generator & Evaluator
Verify that unit and integration tests pass cleanly with 0 regressions.

```bash
uv run pytest
```

**Expected Outcomes**:
- All 74+ tests pass (`74 passed, 0 failed`).
