# Contract: Process Timing & VRAM Offload API

## 1. System Status API (`GET /api/v1/status`)

Exposes system process state, GPU info, and 100% VRAM offload status.

```json
{
  "state": "READY",
  "current_model": "qwen3.5-4b",
  "current_n_ctx": 4096,
  "vram_total": 24000,
  "vram_used": 3950,
  "error_msg": "",
  "gpu_cuda_available": true,
  "vram_offloaded_100pct": true,
  "active_requests": 0,
  "gpu_info": {
    "device_id": 0,
    "name": "NVIDIA GeForce GTX 1080 Ti",
    "total_vram_mb": 11264,
    "free_vram_mb": 7314,
    "driver_version": "580.173.02",
    "cuda_version": "13.0",
    "is_cuda_available": true
  },
  "offload_status": {
    "model_id": "qwen3.5-4b",
    "total_layers": 28,
    "offloaded_layers": 28,
    "is_fully_offloaded": true,
    "offloaded_vram_mb": 3950,
    "has_clip_offload": null
  }
}
```

## 2. K8s & LiteLLM Standard Health Check Endpoints

### A. Liveness Probe (`GET /health/liveness`)

- **200 OK**: FastAPI web server & ProcessManager process loop is alive.
- **503 Service Unavailable**: Server process crashed or internal state corrupted.

```json
{
  "status": "alive",
  "uptime_sec": 1245.2
}
```

### B. Readiness Probe (`GET /health/readiness`)

- **200 OK**: Model is 100% offloaded to VRAM (`vram_offloaded_100pct == True`) AND process status is `READY`.
- **503 Service Unavailable**: Model is currently `LOADING`, `UNLOADED`, or `DOWNLOADING`.

```json
{
  "status": "ready",
  "model_id": "qwen3.5-4b",
  "vram_offloaded_100pct": true
}
```
