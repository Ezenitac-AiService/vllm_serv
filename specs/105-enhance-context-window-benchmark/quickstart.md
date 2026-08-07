# Quickstart & Verification Guide: 컨텍스트 윈도우 크기 벤치마킹 고도화 (105-enhance-context-window-benchmark)

본 가이드는 컨텍스트 윈도우 벤치마크 고도화 기능이 정상 작동하고 기존 캐시 데이터가 안전하게 보호되는지 검증하는 검증 절차를 설명합니다.

---

## Prerequisites

1. 파이썬 가상환경 동기화 완료 (`uv sync`)
2. 로컬 GGUF 모델 가중치 존재 확인 (`models/qwen3.5-2b/Qwen3.5-2B-Q4_K_M.gguf` 등)

---

## Verification Scenarios

### Scenario 1: 단일 소형 모델 정밀 이진 탐색 검증 (`--fine-grained`)

`default_n_ctx` (4096) 캡이 해제되어 탐색 구간이 `[4096, 16384]`로 확대되고, 동적 헬스체크 타임아웃 적용 하에 4096 이상의 가용 컨텍스트 윈도우 크기가 탐색되는지 검증합니다.

```bash
# 1. 정밀 이진 탐색 구동
uv run python scripts/benchmark_context_window.py --model qwen3.5-2b --fine-grained --json

# 2. 검증 기대 항목
# - 로그에 "구간=[4096, 16384]" 표시
# - JSON 출력에 binary_search_steps 배열 및 max_context_length 결과 포함
```

---

### Scenario 2: 빈 보고서 리스트 수신 시 프로필 캐시 원자적 병합 보존 검증

`scripts/benchmark_quality.py` 실행 시 결과가 비어 있더라도 `config/model_context_profiles.json` 파일의 12개 기존 프로필이 유실되거나 초기화되지 않는지 검증합니다.

```bash
# 1. 파이썬 단편으로 빈 보고서 저장 테스트
uv run python -c "from scripts.benchmark_quality import save_context_profiles_cache; save_context_profiles_cache([], {})"

# 2. 출력 로그 확인
# 기대 로그: "[BENCHMARK INFO] ⏩ Empty reports list; preserving existing context profiles cache (config/model_context_profiles.json)."

# 3. 파일 라인 수 및 프로필 보존 확인
grep -c '"max_context_length"' config/model_context_profiles.json
# 기대 결과: 12 (기존 12개 프로필 유지)
```

---

### Scenario 3: 전체 회귀 테스트 통과 검증

```bash
# 전체 Pytest 수트 구동
uv run pytest tests/unit/test_config_manager.py
```
