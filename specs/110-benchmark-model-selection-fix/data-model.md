# Data Model: 벤치마크 파이프라인 최적 모델 및 컨텍스트 윈도우 동적 선정 스키마

**Feature Identifier**: `110-benchmark-model-selection-fix`  
**Date**: 2026-08-07  

---

## 1. Entities & Schema Definitions

### 1.1 Model Benchmark Result Object (`ModelBenchmarkResult`)

`run_fine_grained_binary_search` 및 `evaluate_all_catalog_models`에서 모델별 벤치마크 결과로 다루는 표준 데이터 객체.

| Field Name | Type | Description | Required | Validation / Range |
|------------|------|-------------|----------|-------------------|
| `recommended_model` | `string` | 모델 식별자 (예: `"qwen3.5-4b"`) | Yes | Non-empty string |
| `max_context_length` | `integer` | 이진 탐색으로 실측 통과한 최대 context window | Yes | $\ge 2048$, 512/1024 aligned |
| `recommended_context_length` | `integer` | 서빙 추천 context window 크기 | Yes | $\ge 2048$, 512/1024 aligned |
| `tpot_tok_per_sec` | `float` | 실측 웜업 TPOT (Tokens Per Second) | Yes | $> 0.0$ if supported |
| `peak_vram_mb` | `integer` | 실측 GPU VRAM 점유 피크 (MB) | Yes | $\ge 0$ |
| `is_supported` | `boolean` | GPU 실측 부하 검증 통과 여부 | Yes | `true` / `false` |
| `failure_reason` | `string` | 미지원 사유 (OOM Risk, Timeout 등) | Yes | Default: `"SUCCESS"` |

---

### 1.2 Model Selection Candidate Score Object (`ModelSelectionScore`)

Stage 4 최적 모델 선정을 위해 C-B-A 알고리즘 평가 시 내부 정렬 키로 사용하는 객체.

| Field Name | Type | Description | Formula / Value |
|------------|------|-------------|-----------------|
| `model_name` | `string` | 카탈로그 모델명 | Key string |
| `is_supported` | `boolean` | 실측 벤치마크 성공 여부 | `true` / `false` |
| `rec_ctx` | `integer` | 추천 context window 크기 | `recommended_context_length` |
| `passes_ctx_floor` | `boolean` | 동적 8K/4K/2K 임계값 통과 여부 | `rec_ctx >= active_floor` |
| `param_weight` | `float` | 파라미터 품질 가중치 | 9B/12B: 3.0, 4B: 2.0, 2B: 1.0 |
| `tps` | `float` | 토큰 생성 속도 (TPS) | `tpot_tok_per_sec` |
| `composite_score` | `float` | C-B-A 2단계 복합 평가 점수 | $\text{param\_weight} \times \text{tps} \times \log_2(\text{rec\_ctx} / 2048) / (\text{vram\_mb} / 1024)$ |
| `vram_mb` | `integer` | VRAM 점유량 (MB) | `peak_vram_mb` |

---

## 2. Configuration Persistence Data Model (`server_config.json` & `model_context_profiles.json`)

```json
{
  "recommended_model": "qwen3.5-4b",
  "recommended_context_window": 16384,
  "benchmark_tps": 30.0,
  "vram_used_mb": 4127,
  "evaluated_models": {
    "qwen3.5-4b": {
      "max_context_length": 16384,
      "recommended_context_length": 16384,
      "tpot_tok_per_sec": 30.0,
      "peak_vram_mb": 4127,
      "is_supported": true,
      "failure_reason": "SUCCESS"
    }
  }
}
```
