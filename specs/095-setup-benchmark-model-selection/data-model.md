# Data Model: `setup.sh` 4단계 모듈화 벤치마크 파이프라인 (`095-setup-benchmark-model-selection`)

**Feature**: [`spec.md`](file:///home/dev/storage/vllm_serv/specs/095-setup-benchmark-model-selection/spec.md)  
**Date**: 2026-08-04 | **Amended**: 2026-08-05

---

## Data Entities

### 1. `ModularSetupPipeline` (Pydantic Model)
4단계 모듈식 셋업 파이프라인의 진행 상태 및 벤치마크 결과를 관리하는 데이터 객체.

| Field Name | Type | Description | Validation / Rules |
| :--- | :--- | :--- | :--- |
| `stage_status` | `Dict[str, str]` | 각 Stage (1~4)별 성공/진행/스킵 상태 | `"SUCCESS" \| "FAILED" \| "SKIPPED" \| "WARNING"` |
| `download_ok` | `bool` | Stage 1 모델 다운로드 완료 여부 | `True` when essential models present |
| `integrity_ok` | `bool` | Stage 2 GGUF 헤더 `GGUF` 무결성 검증 여부 | `True` when 4-byte magic signature & size valid |
| `recommended_model` | `str` | Stage 4에서 판정된 최적 서빙 모델명 | Must exist in `model_catalog.json` |
| `recommended_context_window` | `int` | Stage 4에서 판정된 최적 컨텍스트 크기 | Positive integer (e.g., `4096`, `8192`, `12288`) |
| `benchmark_tps` | `float` | Stage 3 실측 생성 토큰 속도 | Tokens / sec (`>= 0.0`) |
| `vram_used_mb` | `int` | Stage 3 실측 피크 VRAM 사용량 | Measured in MB via NVML |
| `benchmark_timestamp` | `str` | 벤치마크 수행 일시 (ISO-8601) | e.g. `2026-08-05T08:00:00Z` |

---

### 2. `FineGrainedContextProfile` (Pydantic Model)
`--fine-grained` 모드 구동 시 2단계 이진 탐색(Binary Search) 정밀 측정 결과를 저장하는 데이터 객체.

| Field Name | Type | Description | Validation / Rules |
| :--- | :--- | :--- | :--- |
| `model_id` | `str` | 대상 모델 식별자 | e.g., `"qwen3.5-4b"` |
| `max_context_length` | `int` | 이진 탐색으로 도출된 최단 1024 해상도 한계 크기 | Positive integer (e.g. `12288`) |
| `recommended_context_length` | `int` | 90% VRAM 마진 고려 안전 추천 크기 | `max(2048, max_context_length * 9 // 10)` |
| `binary_search_steps` | `List[Dict[str, Any]]` | 이진 탐색 각 스텝별 `n_ctx`, `vram_mb`, `status` 기록 | List of step traces |
| `peak_vram_mb` | `int` | 최대 VRAM 사용량 | Measured in MB |
| `tpot_tok_per_sec` | `float` | 실측 평균 TPOT 속도 | Tokens / sec |
| `scaling_tested` | `bool` | 정밀 탐색 완수 여부 | `True` |
| `last_tested_at` | `str` | 정밀 탐색 일시 (ISO-8601) | e.g., `2026-08-05T08:00:00Z` |

---

## Configuration Output Schema (`config/server_config.json`)

```json
{
  "model": "qwen3.5-4b",
  "context_window": 8192,
  "n_gpu_layers": 99,
  "host": "0.0.0.0",
  "port": 8081,
  "auto_benchmark_profile": {
    "recommended_model": "qwen3.5-4b",
    "recommended_context_window": 8192,
    "benchmark_tps": 42.5,
    "vram_used_mb": 4520,
    "benchmark_timestamp": "2026-08-05T08:00:00Z"
  }
}
```

---

## Profile Cache Schema (`config/model_context_profiles.json`)

```json
{
  "generated_at": "2026-08-05T08:00:00Z",
  "system_hardware": {
    "gpu_name": "NVIDIA GeForce GTX 1080 Ti",
    "total_vram_mb": 11264,
    "cuda_version": "13.0",
    "is_cuda_available": true
  },
  "profiles": {
    "qwen3.5-4b": {
      "max_context_length": 12288,
      "recommended_context_length": 8192,
      "peak_vram_mb": 4520,
      "tpot_tok_per_sec": 42.5,
      "scaling_tested": true,
      "last_tested_at": "2026-08-05T08:00:00Z"
    }
  }
}
```
