# Quickstart & Verification Guide: Full Multi-Model GPU Benchmarking

**Feature ID**: 097-multi-model-force-benchmark  

## 1. Multi-Model Forced Benchmark Verification

Run `./setup.sh --force-benchmark` from project root:

```bash
./setup.sh --force-benchmark
```

### Expected Output
- Step 2.8 logs candidate model iteration across catalog models (`qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b`, `gemma4-e2b`, etc.).
- Benchmark metrics (TPS, VRAM) are printed for evaluated candidate models.
- The best performing model is selected and fine-grained binary search calculates its maximum context window.
- `config/server_config.json` is updated with the selected model and context window.

## 2. Direct Python Script Verification

```bash
uv run python scripts/benchmark_context_window.py --force-benchmark
```
