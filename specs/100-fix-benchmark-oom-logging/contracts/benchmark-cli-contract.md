# Interface Contract: Benchmark CLI & Logging Contracts (100-fix-benchmark-oom-logging)

## CLI Contract: `scripts/benchmark_context_window.py`

### Input Arguments

- `--force-benchmark`: 카탈로그 전체 LLM 후보 모델 대상 강제 실측 벤치마킹 구동.
- `--skip-benchmark`: 3단계 실측 벤치마크를 스킵하고 기존 설정 보존.
- `--fine-grained`: 정밀 프로파일링 이진 탐색 모드 구동.
- `--model <MODEL_ID>`: 특정 벤치마크 대상 모델명 (기본값: `config/server_config.json` 내 선언된 기본 모델).
- `--json`: 결과를 JSON 규격으로 표준 출력(stdout)에 출력.

### Output Log Format: `logs/benchmark.log`

```text
[2026-08-05T13:45:00.123456+00:00] [BENCHMARK] [MODEL: qwen3.5-4b] [STEP: 1] Initializing n_ctx=4096 (Estimated Base VRAM: 4200MB)
[2026-08-05T13:45:01.234567+00:00] [llama-server] llama_model_loader: loaded meta data with 24 key-value pairs
[2026-08-05T13:45:05.345678+00:00] [llama-server] llama_kv_cache_init: CUDA0 KV buffer size = 1024.00 MiB
[2026-08-05T13:45:08.456789+00:00] [BENCHMARK] [MODEL: qwen3.5-4b] [STEP: 1] /health check PASSED in 7.2s. Real VRAM: 5220MB. Status: PASS
```

### Output Error Log Format: `logs/error.log`

```text
[2026-08-05T13:45:30.987654+00:00] [Port 8081] [ProcessManager] ❌ 벤치마크 서브프로세스 (PID 12345, Port 8081) 타임아웃/오류 종료. 사유: HEALTH_CHECK_TIMEOUT. 최근 출력:
  llama_model_loader: loaded meta data with 24 key-value pairs
  llama_model_loader: - type  f32:   80 tensors
  llama_kv_cache_init: CUDA0 KV buffer size = 4096.00 MiB
  ggml_cuda_init: allocating 11000 MiB buffer...
  CUDA error: out of memory at ggml-cuda.cu:1234
```

---

## File Contract: `scripts/ensure_models.py`

### Dynamic Catalog Reading Contract

- `ensure_models.py`는 코드 내부의 정적 배열 `REQUIRED_MODELS` 대신 `config/server_config.json`의 `model`, `embedding_model`, `rerank_model` 필드 및 `config/model_catalog.json` 카탈로그 항목에서 동적으로 필수 모델 목록을 수집하여 프로비저닝해야 합니다.
