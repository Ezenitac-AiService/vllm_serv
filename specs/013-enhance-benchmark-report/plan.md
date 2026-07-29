# Implementation Plan: 6-Model Comprehensive Benchmark Report, Qualitative Answer Comparison & Context Window Scaling Enhancement

**Feature Directory**: `specs/013-enhance-benchmark-report`  
**Created Date**: 2026-07-29  
**Status**: Complete (Pure Text LLM Serving & 6-Model Benchmark Integrated)  

---

## 1. Technical Context & Primary Dependencies

- **Language / Framework**: Python 3.12, FastAPI, Pytest, `httpx`, `asyncio`
- **Primary Modules**:
  - `scripts/benchmark_quality.py`: Benchmark execution loop, markdown report generation, 6-model dataset compilation.
  - `src/eval/quality_evaluator.py`: Golden Dataset loader (`data/golden_dataset.json`), ROUGE-L & Exact Match evaluator.
  - `src/core/process_manager.py`: Process spawning, `_wait_for_port_free()`, `stop_process()`, Pure Text LLM mode (`clip_file = None`).
  - `src/core/gpu_detector.py`: PyNVML GPU VRAM detection and OOM threshold computation.
- **Data Storage & Contracts**:
  - `data/golden_dataset.json`: 10 representative prompt-answer ground truth items.
  - `data/reports/analysis_report_quality.md`: Output Markdown benchmark report.
  - `.specify/feature.json`: Active feature directory resolution.

---

## 2. Architecture & Design Principles

1. **Complete 6-Model Reporting Guarantee (FR-001)**:
   - Ensure all 6 models (`gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`, `qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b`) are tracked in `MODELS_CATALOG` and emitted into the comparison table.
   - If a model encounters a spawn failure or timeout, record its status as `FAILED (reason)` in the table instead of omitting the row.

2. **Qualitative Sample Diff & Collapsible Details UX (FR-002, FR-003, FR-004)**:
   - Extend `ComprehensiveQualityReportMetric` data structure to store prompt ID, prompt text, golden reference ground truth, raw model output text, and sub-score metrics (ROUGE-L F1, Exact Match, JSON Schema Pass Rate, Error Tags).
   - Render qualitative sample comparisons using GitHub Markdown `<details><summary>` collapsible tags for optimal readability.

3. **Context Window Scaling & VRAM Safety Threshold (FR-005)**:
   - Benchmark context scaling for `n_ctx` values (`4096`, `8192`, `16384`, `32768`).
   - Track KV cache memory allocation and TTFT latency scaling to compute maximum safe `n_ctx` without OOM on 11GB GTX 1080 Ti hardware.

4. **Multi-Persona Synthesis Integration (FR-006)**:
   - Append 5-persona deep analysis sections (Data Analyst, Deep Learning Expert, Fine-Tuning Expert, DevOps Manager, AI Architect) to the report.

5. **Pure Text LLM Serving & Clip MMProj Bypass (FR-007)**:
   - Bypass `--clip_model_path` multimodal vision projector during LLM process spawn in `src/core/process_manager.py` to eliminate 25~75s loading delays and reduce VRAM footprint for ultra-fast text-only serving.

---

## 3. Plan Phases & Touch-Points

- **Phase 0 (Research)**: `specs/013-enhance-benchmark-report/research.md`
- **Phase 1 (Design & Contracts)**:
  - Data Model: `specs/013-enhance-benchmark-report/data-model.md`
  - Contract: `specs/013-enhance-benchmark-report/contracts/benchmark-report-schema.json`
  - Quickstart: `specs/013-enhance-benchmark-report/quickstart.md`
- **Phase 2 (Implementation Tasks)**:
  - `specs/013-enhance-benchmark-report/tasks.md`
