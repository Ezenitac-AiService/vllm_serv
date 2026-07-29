# Data Model & Configuration Schemas: Feature 016

**Feature**: `specs/016-context-scaling-and-cleanup-fix`
**Date**: 2026-07-29

---

## 1. Entities & Data Structures

### `ContextScalingMetric` (Benchmark Entity)
컨텍스트 크기별 실측 GPU 지표를 담는 엔티티.

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `n_ctx` | `int` | 컨텍스트 윈도우 크기 (2048, 4096, 8192, 16384, 32768) |
| `peak_vram_mb` | `int` | 실측 Peak VRAM 사용량 (MB) |
| `ttft_ms` | `float` | 첫 토큰 도달 시간 (ms) |
| `tpot_tok_per_sec` | `float` | 토큰 생성 속도 (tok/s) |
| `is_oom` | `bool` | VRAM 11GB 초과 또는 OOM 발생 여부 |

---

### `OptimalModelRecommendation` (Recommendation Entity)
워크로드 유형별 최적 모델 및 컨텍스트 추천 엔티티.

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `workload_type` | `str` | 워크로드 (⚡ 초저지연 에이전트 / ⚖️ 기본 상주 서빙 / 🎯 고정밀 분석) |
| `recommended_model` | `str` | 추천 모델 ID (예: `qwen3.5-4b`) |
| `recommended_n_ctx` | `int` | 추천 컨텍스트 크기 (예: `8192`) |
| `reasoning` | `str` | 선정 사유 |

---

### `ModelCatalogEntry` (JSON Catalog Entity)
`config/model_catalog.json`에 정의되는 모델 엔티티.

```json
{
  "model_id": "gemma4-e2b",
  "name": "Gemma 4 E2B",
  "repo_id": "ggml-org/gemma-4-E2B-it-GGUF",
  "filename": "gemma-4-E2B_q4_0-it.gguf",
  "clip_filename": "gemma-4-E2B-it-mmproj.gguf",
  "target_dir": "models/gemma4-2b",
  "chat_template": "gemma",
  "default_n_ctx": 4096,
  "vram_est_mb": 3500,
  "requires_mmproj": true
}
```

---

### `OpenAIModelObject` (OpenAI API Model Entity)
`GET /v1/models` 응답 규격 엔티티.

```json
{
  "id": "gemma4-e2b",
  "object": "model",
  "created": 1770000000,
  "owned_by": "llm-server",
  "permission": [],
  "is_available": true,
  "is_active": false
}
```
