# Technical Research: Multi-Model GPU Benchmarking Heuristics

**Feature ID**: 097-multi-model-force-benchmark  

## 1. Candidate LLM Iteration Strategy
- Scan `config/model_catalog.json` for all LLM entries (`requires_mmproj: false` or task type LLM, excluding embedding/reranker).
- Filter candidate models by local file availability in `models/` (or auto-download if enabled).
- Benchmark each candidate model using `ProcessManager` warm-up (e.g. 50 tokens generated).
- Collect Peak VRAM (NVML) and Token Generation Speed (TPS).

## 2. Selection Heuristic
- **VRAM Boundary**: Filter out models whose VRAM footprint exceeds available GPU VRAM (e.g., 11264 MB for GTX 1080 Ti).
- **Throughput Priority**: Select the candidate model achieving maximum TPS within safe VRAM capacity.
- **Fine-Grained Context Binary Search**: Perform 512/1024-step binary search for the selected model to determine maximum context window length.
