# Quickstart Validation Guide: 컨텍스트 윈도우 벤치마크 동적 KV 캐시 오탐 수정 및 카탈로그 전수 평가

## Prerequisites

- Python 3.12+ 가상환경 (`uv`)
- NVIDIA GPU (RTX 3060 12GB VRAM 이상) 또는 MOCK 환경 (`MOCK_LLAMA_SERVER=1`, `MOCK_BENCHMARK_TPS=30.0`)

---

## Scenario 1: GQA 아키텍처 기반 동적 KV 캐시 VRAM 계산 및 16K 사전 스폰 통과 검증

소형/GQA 모델(Qwen 3.5 2B/4B)에 대해 `estimate_vram_usage(model_id, n_ctx=16384)` 계산 시 15.2GB 오탐 대신 실제 VRAM 사용량이 정확히 계산되어 사전 스폰이 허용되는지 단정 테스트를 수행합니다.

### Run Command

```bash
uv run pytest tests/unit/test_benchmark_context_window.py -k test_estimate_vram_usage_uses_model_gqa_architecture
```

### Expected Outcome

- `test_estimate_vram_usage_uses_model_gqa_architecture` 100% PASS.
- Qwen 3.5 2B @ `n_ctx=16384` 산출 VRAM이 11,264MB 이하(약 3,500MB 내외)로 계산되어 `is_supported=True`로 스폰 가능 상태 판정.

---

## Scenario 2: CLI 전수 카탈로그 평가 모드 (`--all`) 실측 동작 검증

카탈로그 내 전체 LLM 모델에 대해 순차 이진 탐색 프로파일링을 수행하고 `config/model_context_profiles.json` 프로파일 저장을 확인합니다.

### Run Command

```bash
MOCK_LLAMA_SERVER=1 uv run python scripts/benchmark_context_window.py --fine-grained --all
```

### Expected Outcome

- 콘솔 출력: `[BENCHMARK INFO] 🚀 카탈로그 전체 LLM 후보 모델 전수 이진 탐색 평가 개시`
- 카탈로그 내 모든 가용 모델(`qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b`, `gemma4-e2b`, `gemma4-e4b` 등)이 순차적으로 탐색 및 갱신됨.
- `config/model_context_profiles.json` 파일에 모든 가용 모델의 프로파일 키 생성 완료.

---

## Scenario 3: 종합 품질-컨텍스트 벤치마크 (`benchmark_quality.py`) 16K 구간 측정 검증

### Run Command

```bash
MOCK_LLAMA_SERVER=1 uv run python scripts/benchmark_quality.py
```

### Expected Outcome

- [Step 5.1] 스케일링 측정 루프에서 일률적인 `15216MB exceeds GPU capacity limit` 오탐 스폰 실패 발생 0건.
- `data/reports/analysis_report_quality.md` 생성 완료.

---

## Scenario 4: 전체 단위 테스트 수트 회귀 검증

```bash
uv run pytest tests/unit/ --ignore=tests/unit/test_legacy_extraction_llm.py --ignore=tests/unit/test_e2e_serving.py --ignore=tests/unit/test_embedding_reranker_serving.py
```

### Expected Outcome

- 340+ 개 전체 단위 테스트 100% PASS.
