# Runnable Quickstart Guide: Real GPU Benchmark Engine & Dual-Mode Test Framework

**Feature Directory**: `specs/014-real-gpu-benchmark-testing`  
**Created Date**: 2026-07-29  

---

## 1. Environment & Prerequisites

- **Python**: 3.12+ managed via `uv`
- **GPU Hardware**: NVIDIA GeForce GTX 1080 Ti (11GB VRAM) or CUDA-capable NVIDIA GPU
- **Dependencies**: `llama-cpp-python`, `pynvml`, `pytest`, `httpx`, `fastapi`

---

## 2. Execution Scenarios

### Scenario 1: One-Stop Auto-Download + Real GPU Inference Benchmark Loop

Run full 6-model benchmark on live GPU:

```bash
uv run python scripts/benchmark_quality.py --auto-download --real
```

**Expected Outcome**:
1. Verifies/compiles CUDA `llama-server` binary into `.bin/llama-server`.
2. Downloads missing GGUF models from HuggingFace Hub.
3. Sequentially spawns `llama-server` for all 6 catalog models (`gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`, `qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b`).
4. Performs real HTTP inference requests, metrics calculation, and generates `specs/013-enhance-benchmark-report/analysis_report_quality.md` and `data/reports/analysis_report_quality.md`.
5. Restores resident default model (`qwen3.5-4b`).

---

### Scenario 2: Quick Pytest Unit Suite (Mock Mode)

Run fast unit tests without launching real GPU processes:

```bash
uv run pytest tests/unit/ -v
```

**Expected Outcome**:
- Executes unit tests in Mock Mode (`TEST_MODE=mock`) in < 5 seconds with 100% pass rate.

---

### Scenario 3: Real GPU Integration Suite (`pytest --real`)

Run integration tests against real CUDA `llama-server` subprocesses:

```bash
uv run pytest tests/integration/ -v --real
```

**Expected Outcome**:
- Pytest inspects `--real` flag, sets `TEST_MODE=real`, un-mocks process managers, spawns real `llama-server` instances, and validates real VRAM offloading and HTTP `/v1/chat/completions` REST API responses.
