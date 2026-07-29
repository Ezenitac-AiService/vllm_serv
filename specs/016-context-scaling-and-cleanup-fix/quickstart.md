# Quickstart Validation Guide: Feature 016

**Feature**: `specs/016-context-scaling-and-cleanup-fix`
**Date**: 2026-07-29

---

## 1. Automated Test Suite Validation

```bash
# Execute unit & integration test suite
uv run pytest -v
```

**Expected Outcome**: 100% tests pass (83+ passed, 0 failed).

---

## 2. OpenAI `GET /v1/models` API Validation

```bash
# Start microservice server
uv run python -m src.api.main
```

In a second terminal:
```bash
curl -X GET http://127.0.0.1:8000/v1/models
```

**Expected Outcome**:
```json
{
  "object": "list",
  "data": [
    {
      "id": "gemma4-e2b",
      "object": "model",
      "created": 1770000000,
      "owned_by": "llm-server",
      "is_available": true,
      "is_active": false
    },
    ...
  ]
}
```

---

## 3. Real GPU Multi-Context Scaling & Clean Exit Benchmark Validation

```bash
# Run real GPU multi-context benchmark
PYTHONUNBUFFERED=1 uv run python -u scripts/benchmark_quality.py --auto-download --real
```

**Expected Outcome**:
1. All 6 models benchmarked across `n_ctx` (2K, 4K, 8K, 16K, 32K) without OOM crashes.
2. Report generated at `data/reports/analysis_report_quality.md` with Scaling Comparison Table and Optimal Model Recommendation Matrix.
3. Zero `BaseSubprocessTransport.__del__ RuntimeError: Event loop is closed` warnings on exit.
