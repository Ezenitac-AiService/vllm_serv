# Research: GPU VRAM Offload & Process Lifecycle Timing Fix

## Research Questions & Decisions

### 1. GPU VRAM 100% Offload Readiness Verification Strategy

- **Problem**: `llama-server` binds port 8081 and responds with HTTP 200 OK on `/v1/models` in ~0.06 seconds during process initialization *before* CUDA tensors are fully allocated to GPU VRAM. This caused `LlamaManager` to prematurely mark the process `READY`, leading to early inference calls falling back to CPU RAM.
- **Decision**: Update `_wait_for_ready()` and `_monitor_process()` in `LlamaManager` to require BOTH HTTP `/health` JSON endpoint status (`{"status": "ok"}`) AND `vram_offloaded_100pct == True` (verified via stdout log parsing) before transitioning process state to `READY`. Expose K8s & LiteLLM-compatible `/health/liveness` and `/health/readiness` endpoints in FastAPI.
- **Rationale**: Relying solely on `/v1/models` HTTP polling is insufficient for C++ GGUF backend binaries that start their HTTP event loop before completing GGML tensor offloading. Native `/health` API plus log parsing ensures double verification.
- **Alternatives Considered**:
  - *Fixed sleep delay (e.g. 5 seconds)*: Rejected because loading times differ significantly across 2B (1s) vs 12B (8s+) models.

### 2. PyNVML Non-blocking VRAM Inspection & Socket Isolation

- **Problem**: Subprocess `nvidia-smi` execution in `asyncio` event loops blocks the main thread for 100-300ms. Also, port socket cleanup must prevent TCP `TIME_WAIT` re-binding races.
- **Decision**:
  - Use `pynvml` (NVIDIA Management Library Python Bindings) for direct C-API VRAM inspection (< 1ms execution time) with fallback to `nvidia-smi`.
  - Enforce synchronous step-by-step teardown in `ProcessManager.stop_process()`:
    1. **Graceful Stream Drain Phase**: Wait for active streaming requests (`active_requests == 0`, max 5s timeout).
    2. Escalated process termination (SIGTERM -> 5s timeout -> SIGKILL).
    3. Socket port release verification with `SO_REUSEADDR` socket option check.
    4. PyNVML VRAM baseline check (`verify_vram_released()`).
- **Rationale**: Direct C-API memory queries prevent event loop freezing during continuous status polling, while stream drain prevents dropping active client connection tokens during hot-swaps.

### 3. GGUF + KV Cache Pre-flight VRAM Estimator (Ollama / LM Studio Pattern)

- **Problem**: Large context sizes ($n_{ctx} \ge 8192$) allocate significant VRAM for KV Cache. Checking model file weight size alone leads to unexpected OOM when launching inference.
- **Decision**: Implement mathematical KV Cache memory estimation prior to `subprocess.exec`:
  $$VRAM_{total} = VRAM_{weight} + (2 \cdot n_{layers} \cdot n_{heads} \cdot d_{head} \cdot n_{ctx} \cdot \text{bytes\_per\_elem})$$
- **Rationale**: Prevents launching `llama-server` when estimated KV Cache memory exceeds total GPU VRAM capacity.

### 4. Normal Serving Operational Mode vs. Benchmark Lifecycle (Model Load/Unload Timing)

- **Problem**: Clarifying when model load, unload, and VRAM release should happen during daily serving vs. benchmark runs.
- **Decision**:
  - **Normal Serving Mode**: The server (`src/api/server.py`) keeps the default resident model (`qwen3.5-4b`) **permanently on-loaded in GPU VRAM**. No per-request load/unload occurs. VRAM is continuously occupied for instant user chat inference.
  - **Model Hot-Swap**: Unload and VRAM release happen ONLY when an explicit API request (`POST /api/v1/models/load`) or CLI switch is triggered.
  - **Benchmark Lifecycle**: When `scripts/benchmark_quality.py` executes:
    1. Safely unload the default resident model and release VRAM.
    2. Sequentially test each model (load -> verify 100% VRAM offload & `/health` JSON -> run inference -> unload & release VRAM).
    3. Upon benchmark completion, **automatically restore (re-load) the default resident model (`qwen3.5-4b`)** back into VRAM to resume normal serving.
- **Rationale**: User chat serving demands zero cold-start latency (permanent VRAM residency), while benchmarking requires isolated clean VRAM measurement for each candidate model and clean restoration of normal serving post-test.
