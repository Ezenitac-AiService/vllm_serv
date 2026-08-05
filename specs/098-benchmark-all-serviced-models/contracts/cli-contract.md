# Interface Contract: benchmark_context_window.py & setup.sh CLI Contract

**Feature**: `098-benchmark-all-serviced-models`
**Created**: 2026-08-05

## 1. CLI Executable Contract (`scripts/benchmark_context_window.py`)

### Command Invocation
```bash
uv run python scripts/benchmark_context_window.py [OPTIONS]
```

### Options Specification

| Option Flag | Type | Default | Description | Execution Flow |
|-------------|------|---------|-------------|----------------|
| `--force-benchmark` | Flag | `False` | 카탈로그 전체 LLM 모델 대상 강제 실측 벤치마크 수행 | 모든 LLM 후보 모델에 대해 실제 GPU 프로세스 스폰 및 이진 탐색 스케일링을 순차 실행 후 `model_context_profiles.json` 덮어쓰기 |
| `--fine-grained` | Flag | `False` | 2단계 이진 탐색(512/1024 토큰 얼라인먼트) 정밀 프로파일링 구동 | 지정된 모델 또는 캐시 미스 모델 대상 이진 탐색 실행 |
| `--model` | String | `"qwen3.5-4b"` | 단일 벤치마크 대상 모델명 | 단일 지정 모델에 대해 벤치마크 수행 |
| `--skip-benchmark` | Flag | `False` | 3단계 실측 벤치마크 스킵 및 기존 프로필 보존 | 실측 스킵 후 5초 이내 exit 0 종료 |
| `--json` | Flag | `False` | 벤치마크 최종 결과를 JSON 표준 출력으로 반환 | stdout에 JSON payload 출력 |

### Output JSON Schema Example (`--json` 사용 시)
```json
{
  "recommended_model": "gemma4-e2b",
  "recommended_context_window": 3584,
  "benchmark_tps": 45.0,
  "vram_used_mb": 4200,
  "evaluated_models": {
    "gemma4-e2b": {
      "recommended_model": "gemma4-e2b",
      "recommended_context_window": 3584,
      "benchmark_tps": 45.0,
      "vram_used_mb": 4200
    },
    "qwen3.5-4b": {
      "recommended_model": "qwen3.5-4b",
      "recommended_context_window": 8192,
      "benchmark_tps": 42.0,
      "vram_used_mb": 4500
    }
  },
  "stage_status": {
    "Stage 1": "SUCCESS",
    "Stage 2": "SUCCESS",
    "Stage 3": "SUCCESS (Multi-Model Catalog Forced Real GPU Benchmark)",
    "Stage 4": "SUCCESS"
  }
}
```

---

## 2. Shell Script Execution Flow Contract (`scripts/setup.sh`)

### Stage 2.8 & Stage 4.5 Execution Mapping

```bash
# setup.sh 내 Step 2.8 및 Step 4.5 호출 시
if [ "$FORCE_BENCHMARK" -eq 1 ]; then
    log_info "🔥 --force-benchmark 옵션 감지: 카탈로그 전체 LLM 후보 모델 대상 강제 실측 벤치마킹 수행 중..."
    "$VENV_PYTHON" "$BASE_DIR/scripts/benchmark_context_window.py" --force-benchmark
elif [ "$SKIP_BENCHMARK" -eq 1 ]; then
    log_info "⏩ --skip-benchmark 옵션 감지: 3단계 실측 벤치마크 스킵..."
    "$VENV_PYTHON" "$BASE_DIR/scripts/benchmark_context_window.py" --skip-benchmark
else
    # 일반 구동: 부분 캐시 미스 감지 및 스킵 제어 내부 수행
    "$VENV_PYTHON" "$BASE_DIR/scripts/benchmark_context_window.py"
fi
```

### Exit Codes & Failure Handlers

* `0`: 벤치마크 및 설정 반영 성공 (또는 스킵 성공).
* `1`: 심각한 시스템 에러 (파이썬 가상환경/CUDA 미설치 등). *단, 개별 모델의 OOM/타임아웃은 0을 유지하고 해당 모델만 `unsupported` 마킹*.
