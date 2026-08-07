# CLI Contract: 벤치마크 파이프라인 CLI 및 C-B-A 최적 모델 선정 계약

**Feature Identifier**: `110-benchmark-model-selection-fix`  
**Date**: 2026-08-07  

---

## 1. CLI Execution Contract (`scripts/benchmark_context_window.py`)

### Command Signature
```bash
uv run python scripts/benchmark_context_window.py [OPTIONS]
```

### Options Contract
- `--force-benchmark`: 카탈로그 내 전체 LLM 후보 모델 대상 실측 벤치마크 및 C-B-A 알고리즘 최적 서빙 모델/컨텍스트 선정 수행.
- `--fine-grained`: `--model <NAME>` 대상 2단계 정밀 이진 탐색 프로파일링 수행.
- `--force-overwrite-profiles`: 기존 검증된 프로파일 덮어쓰기 허용.
- `--json`: 실행 결과를 JSON 포맷으로 표준 출력(stdout) 출력.

---

## 2. Output Schema Contract (Stage 4 Output)

```json
{
  "recommended_model": "<MODEL_NAME>",
  "recommended_context_window": <INT_DYNAMIC_CTX>,
  "benchmark_tps": <FLOAT_TPS>,
  "vram_used_mb": <INT_VRAM_MB>,
  "evaluated_models": { ... },
  "stage_status": {
    "Stage 1": "SUCCESS",
    "Stage 2": "SUCCESS",
    "Stage 3": "SUCCESS (Multi-Model Catalog Forced Real GPU Benchmark)",
    "Stage 4": "SUCCESS"
  }
}
```

### Console Output Contract
```text
[BENCHMARK INFO] 🏆 전체 후보 모델 실측 평가 완료! 최적 서빙 모델 선정: <MODEL_NAME> (TPS: <TPS>)
 Stage 4 (최적 모델 선정 & 설정 반영): ✓ PASSED (모델=<MODEL_NAME>, ctx=<DYNAMIC_CTX>)
```
