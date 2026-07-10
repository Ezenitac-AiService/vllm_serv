# Quickstart: Context Scaling Benchmark

## Prerequisites
- `vllm_serv` project setup with `llama-cpp-python` installed.
- Models (e2b, e4b, 12b) available in the models directory.

## Running the Benchmark

Execute the benchmark script from the project root:

```bash
cd /home/dev/vllm_serv
PYTHONPATH=. python3 src/scripts/benchmark_context_scaling.py
```

## Expected Outcome

1. The script will sequentially test `gemma4-2b`, `gemma4-4b`, and `gemma4-12b`.
2. For each model, it will start at 8K context and increase by 1K increments.
3. At each step, it will output the VRAM usage, TTFT, TPOT, and Needle in a Haystack accuracy.
4. If a model encounters an OOM error or TTFT > 60 seconds, it will gracefully stop and move to the next model.
5. All results are saved in `specs/003-context-scaling/results.jsonl`.
