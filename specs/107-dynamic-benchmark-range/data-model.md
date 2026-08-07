# Data Model: 동적 모델-KV 메모리 기반 벤치마크 탐색 구간 자동 산정 (Dynamic Benchmark Range)

**Feature**: `107-dynamic-benchmark-range`
**Date**: 2026-08-07

## 1. DynamicBenchmarkRangeContext (엔티티 규격)

| Field Name | Type | Description | Validation Rules |
|---|---|---|---|
| `model_id` | `str` | 모델 식별자 (예: `gemma4-e2b`) | 필수 |
| `total_vram_mb` | `int` | 물리 GPU 전체 VRAM (MB) | > 0 |
| `free_vram_mb` | `int` | NVML 실시간 가용 VRAM (MB) | >= 0 |
| `base_vram_mb` | `int` | 모델 파일 및 멀티모달 CLIP 로딩 VRAM | > 0 |
| `safety_margin_mb` | `int` | $500 + \lfloor n_{\text{ctx}} \times 0.05 \rfloor$ | >= 500 |
| `usable_kv_budget_mb` | `int` | `free_vram_mb - base_vram_mb - safety_margin_mb` | >= 0 |
| `max_allocatable_n_ctx` | `int` | KV budget으로 수용 가능한 최대 블록 컨텍스트 | 512 알라인 |
| `model_max_n_ctx` | `int` | 카탈로그 / GGUF 헤더 Max RoPE 한계 | > 0 |
| `dynamic_high_bound` | `int` | $\min(\text{model\_max\_n\_ctx}, \text{max\_allocatable\_n\_ctx})$ | >= low |
| `dynamic_low_bound` | `int` | 2048 또는 수용 최저 블록 | <= high |

---

## 2. VramSettlingStatus (VRAM 수렴 스냅샷 엔티티)

| Field Name | Type | Description | Validation Rules |
|---|---|---|---|
| `attempt_count` | `int` | 수렴 측정 시도 횟수 | 1..5 |
| `last_free_vram_mb` | `int` | 이전 측정 Free VRAM | MB |
| `current_free_vram_mb`| `int` | 현재 측정 Free VRAM | MB |
| `delta_mb` | `int` | `abs(current - last)` | < 10MB 수렴 판정 |
| `is_settled` | `bool` | 연속 2회 수렴 여부 | `True` 시 종료 |

---

## 3. RealInferenceMetrics (실측 TPS 엔티티)

| Field Name | Type | Description | Validation Rules |
|---|---|---|---|
| `prompt_tokens` | `int` | 프롬프트 토큰 수 | > 0 |
| `completion_tokens` | `int` | 생성된 반환 토큰 수 | > 0 |
| `elapsed_seconds` | `float` | 인퍼런스 수행 소요 시간(초) | > 0.0 |
| `measured_tps` | `float` | `completion_tokens / elapsed_seconds` | > 0.0 |
