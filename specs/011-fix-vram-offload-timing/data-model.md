# Data Model: GPU VRAM Offload & Process Lifecycle Timing Fix

## Core Entities & State Specifications

### 1. ProcessStatusEnum & ProcessState

Represents the updated subprocess state transitions for `llama-server`.

```text
[UNLOADED] ---> (spawn_process) ---> [LOADING] ---> (vram_offloaded=True & /health ok) ---> [READY (Permanent Resident)]
    ^                                   |                                                          |
    |                                   v                                                          v
(stop_process) <----------------- [ERROR] <--------------------------------------------------------+
```

#### Fields

- `status`: `ProcessStatusEnum` (UNLOADED, DOWNLOADING, LOADING, READY, ERROR)
- `model_id`: `Optional[str]` - Current loaded model identifier (Default resident: `qwen3.5-4b`)
- `port`: `Optional[int]`
- `pid`: `Optional[int]`
- `error_message`: `Optional[str]`
- `exit_code`: `Optional[int]`
- `vram_offloaded`: `Optional[bool]` - Set to `True` ONLY after 100% VRAM offload is verified via stdout log parsing.
- `active_requests`: `int = 0` - Active streaming HTTP requests count for Graceful Drain.

### 2. VramLoadTimingGuard & ServingModeState

Internal tracking entity for process teardown, VRAM release verification, and mode restoration.

#### Fields

- `default_resident_model`: `str = "qwen3.5-4b"` - Default model for normal serving mode.
- `serving_mode`: `str` - "NORMAL" (permanent VRAM resident) vs. "BENCHMARK" (sequential model test mode).
- `baseline_vram_free_mb`: `int` - Available VRAM measured before model loading.
- `kv_cache_vram_est_mb`: `int` - Calculated KV cache VRAM size ($2 \cdot L \cdot H \cdot D \cdot n_{ctx}$).
- `offload_verified_at`: `Optional[float]` - Timestamp when 100% VRAM offload log was captured.
- `port_freed_at`: `Optional[float]` - Timestamp when port 8081 socket connection was verified free.
- `vram_released`: `bool` - True if VRAM returned to baseline memory.
