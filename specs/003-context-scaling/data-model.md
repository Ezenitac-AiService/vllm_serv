# Phase 1: Data Model

## Benchmark Result Schema (JSONL)

Each line in `results.jsonl` will be a JSON object with the following structure:

```json
{
  "timestamp": "2026-07-10T13:00:00Z",
  "model_id": "gemma4-2b",
  "context_size_k": 8,
  "prompt_tokens": 8050,
  "peak_vram_mb": 7032,
  "ttft_ms": 1250,
  "tpot_ms": 25.4,
  "accuracy": 1.0,
  "status": "SUCCESS"
}
```

- `status` can be `"SUCCESS"`, `"OOM_ERROR"`, or `"TIMEOUT_ERROR"`.
- `accuracy` is `1.0` if the Needle was correctly extracted, `0.0` otherwise.

## Internal Objects
- `BenchmarkRunner`: Manages the loop across models and context sizes.
- `NeedleGenerator`: Generates synthetic background text and inserts the needle at a random depth.
