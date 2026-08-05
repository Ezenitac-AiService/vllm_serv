# Feature Specification: Full Multi-Model GPU Benchmarking & Forced Optimization Pipeline

**Feature ID**: 097-multi-model-force-benchmark  
**Created**: 2026-08-05  
**Status**: APPROVED  

---

## 💡 Overview & User Value

### Problem Statement
When `./setup.sh --force-benchmark` was executed, the script only benchmarked a single default model (`qwen3.5-4b`) rather than iterating through all candidate LLM models registered in `config/model_catalog.json` (such as `qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b`, `gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`). Users expect `--force-benchmark` to evaluate all available candidate models via real GPU load testing, select the optimal serving model based on TPS/VRAM metrics, and determine its maximum context window.

### User Value
Deployment engineers get an automated, exhaustive multi-model benchmark pipeline that selects the best LLM model for the specific host GPU hardware (e.g. GTX 1080 Ti 11GB VRAM, RTX 3060 12GB VRAM) and configures optimal context windows dynamically.

---

## 🎯 Functional Requirements (FR)

- **FR-001**: `--force-benchmark` flag MUST force `benchmark_context_window.py` to iterate through all registered candidate LLM models in `config/model_catalog.json`.
- **FR-002**: For each candidate LLM model, the system MUST perform real GPU load testing (ProcessManager warm-up, NVML VRAM telemetry, TPS calculation).
- **FR-003**: The system MUST compare candidate model benchmark results, automatically select the optimal serving model, and compute its maximum context window length via fine-grained binary search.
- **FR-004**: The system MUST atomically save the selected model and context window into `config/server_config.json` and update `config/model_context_profiles.json`.
- **FR-005**: Step 2.8 and Step 4.5 in `setup.sh` MUST pass `--force-benchmark` down to Python benchmarking scripts to ensure multi-model evaluation is triggered end-to-end.

---

## 🎯 Success Criteria (SC)

- **SC-001**: `./setup.sh --force-benchmark` evaluates all available LLM models in `config/model_catalog.json` and outputs a benchmark comparison table.
- **SC-002**: The optimal model and fine-grained binary search context length are saved atomically into `config/server_config.json`.
- **SC-003**: Unit test suite passes without regressions (`uv run pytest tests/unit/test_setup_benchmark_integration.py`).

---

## 👥 User Scenarios & Acceptance Criteria

### Scenario 1: Multi-Model Forced Benchmark Execution
**Given** the user runs `./setup.sh --force-benchmark`  
**When** the pipeline reaches Step 2.8 and Step 4.5  
**Then** all candidate LLM models in `config/model_catalog.json` are benchmarked via real GPU process load, the optimal model is selected, its fine-grained maximum context window is calculated, and `config/server_config.json` is updated cleanly.

---

## 🧪 Specification Quality Checklist

- [x] No implementation details in core requirements
- [x] Testable and unambiguous acceptance scenarios
- [x] Measurable success criteria
- [x] Bounded feature scope
