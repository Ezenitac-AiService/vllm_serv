# Implementation Plan: Full Multi-Model GPU Benchmarking & Forced Optimization Pipeline

**Feature ID**: 097-multi-model-force-benchmark  
**Branch**: 097-multi-model-force-benchmark  
**Created**: 2026-08-05  

---

## Technical Context

- **Target Script**: `scripts/benchmark_context_window.py` and `scripts/setup.sh`
- **Catalog Source**: `config/model_catalog.json` (all candidate LLMs: `qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b`, `gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`)
- **GPU Warmup & Process Spawning**: `src/core/process_manager.py` (real llama-server instances)
- **NVML Telemetry**: Peak VRAM and TPS measurement
- **Output Target**: `config/server_config.json` & `config/model_context_profiles.json`

---

## Constitution Check

- **Principle I (Quality First)**: Exhaustive candidate evaluation rather than single-model hardcoded fallbacks.
- **Principle II (Strict Verification)**: NVML VRAM peak readout and TPS telemetry validation.

---

## Proposed Touch-points

- `scripts/benchmark_context_window.py`:
  - Add `--all-models` or `--force-benchmark` mode to iterate over all candidate LLM models in `config/model_catalog.json`.
  - Perform real GPU load benchmark for each candidate model, compare TPS/VRAM metrics, select the optimal model, and calculate maximum context window via fine-grained binary search.
- `scripts/setup.sh`:
  - Pass `--force-benchmark` flag to `scripts/benchmark_context_window.py` in Step 2.8 and Step 4.5.
- `tests/unit/test_setup_benchmark_integration.py`:
  - Add unit test for `--force-benchmark` multi-model catalog iteration.

---

## Design Artifacts

- `research.md`: Multi-model GPU evaluation matrix & model selection heuristic.
- `quickstart.md`: Run verification `./setup.sh --force-benchmark`.
