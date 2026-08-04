# Data Model: `setup.sh` 4단계 모듈화 벤치마크 파이프라인 (`095-setup-benchmark-model-selection`)

**Feature**: [`spec.md`](file:///home/dev/storage/vllm_serv/specs/095-setup-benchmark-model-selection/spec.md)  
**Date**: 2026-08-04

---

## Data Entities

### 1. `ModularSetupPipeline` (Pydantic Model)
4단계 모듈식 셋업 파이프라인의 진행 상태 및 벤치마크 결과를 관리하는 데이터 객체.

| Field Name | Type | Description | Validation / Rules |
| :--- | :--- | :--- | :--- |
| `stage_status` | `Dict[str, str]` | 각 Stage (1~4)별 성공/진행/스킵 상태 | `"SUCCESS" \| "FAILED" \| "SKIPPED"` |
| `download_ok` | `bool` | Stage 1 모델 다운로드 완료 여부 | `True` when essential models present |
| `integrity_ok` | `bool` | Stage 2 GGUF 파일 무결성 검증 여부 | `True` when headers & signatures valid |
| `recommended_model` | `str` | Stage 4에서 판정된 최적 서빙 모델명 | Must exist in `model_catalog.json` |
| `recommended_context_window` | `int` | Stage 4에서 판정된 최적 컨텍스트 크기 | One of `[2048, 4096, 8192, 16384, 32768]` |
| `benchmark_tps` | `float` | Stage 3 실측 생성 토큰 속도 | Tokens / sec (`>= 0.0`) |
| `vram_used_mb` | `int` | Stage 3 실측 피크 VRAM 사용량 | Measured in MB |
| `benchmark_timestamp` | `str` | 벤치마크 수행 일시 (ISO-8601) | e.g. `2026-08-04T08:16:00Z` |

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
    "benchmark_timestamp": "2026-08-04T08:16:00Z"
  }
}
```
