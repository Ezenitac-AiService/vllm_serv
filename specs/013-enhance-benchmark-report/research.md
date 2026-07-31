# Research & Technical Decisions: 6-Model Benchmark Report & Qualitative Comparison Enhancement

**Feature Directory**: `specs/013-enhance-benchmark-report`  
**Created Date**: 2026-07-29  

---

## Technical Decisions

### Decision 1: 6-Model Reporting Guarantee & Exception Fallback in Tables
- **Decision**: `scripts/benchmark_quality.py` loop will catch model-level errors, populate a `ComprehensiveQualityReportMetric` object with `is_oom=True` or `error_message`, and guarantee 6 rows in the Markdown output table.
- **Rationale**: Omitting failed models creates confusion for operators. Exhibiting status `FAILED (PortCollision / Timeout / OOM)` explicitly indicates hardware limits or infrastructure errors.

### Decision 2: Qualitative Answer Comparison Data Model & Collapsible UI
- **Decision**: Extend `ComprehensiveQualityReportMetric` with `qualitative_samples: List[QualitativeSampleComparison]`.
- **Rationale**: Storing `prompt_text`, `golden_ground_truth`, `model_response`, `rouge_l_f1`, `exact_match`, `json_valid`, and `error_tags` (`[JSON Format Failure]`, `[Entity Hallucination]`, etc.) enables precise side-by-side rendering under `<details><summary>` tags without inflating top-level table size.

### Decision 3: Context Window Capacity & VRAM Scaling Curve Benchmark
- **Decision**: Add `context_scaling_metrics: List[ContextScalingMetric]` tracking Peak VRAM (MB) and TTFT (ms) across `n_ctx` steps (`4K`, `8K`, `16K`, `32K`).
- **Rationale**: 11GB GTX 1080 Ti hardware VRAM ceiling limits 9B/12B models at high context sizes. Explicitly measuring VRAM scaling curves identifies the exact `VRAM Safety Threshold` (maximum usable `n_ctx`) for production deployment.

### Decision 4: 5-Persona Deep Analysis Section Auto-Generator
- **Decision**: Append a dedicated Markdown section synthesizing Data Analyst, Deep Learning Expert, LLM Fine-Tuning Expert, DevOps Manager, and AI Solution Architect perspectives.
- **Rationale**: Delivers actionable business decision frameworks directly to stakeholders alongside raw benchmark metrics.
