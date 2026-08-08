# Quickstart Validation Guide: VRAM 사전 검증 및 자동 스킵 (Benchmark VRAM Pre-check)

**Feature Directory**: `specs/112-benchmark-vram-precheck`

---

## Runnable Validation Scenarios

### Scenario 1: VRAM 초과 대형 모델 사전 스킵 실측 검증

1. **실행 명령**:
   ```bash
   uv run python scripts/benchmark_quality.py --auto-download --real
   ```
2. **기대 결과**:
   - `gemma4-26b-a4b` 및 `qwen3.6-27b` 등 VRAM > 11GB 모델에 진입할 때 16GB+ GGUF 가중치 다운로드를 시작하지 않고 `[SKIP VRAM OOM Risk]` 경고 출력 후 즉시 다음 수용 가능한 모델로 진입.
   - 네트워크 다운로드 시간 낭비 없이 수용 가능 모델에 대한 벤치마크 평가를 완결.

---

### Scenario 2: VRAM 검사 강제 우회 (`--ignore-vram-check`) 검증

1. **실행 명령**:
   ```bash
   uv run python scripts/benchmark_quality.py --auto-download --ignore-vram-check
   ```
2. **기대 결과**:
   - VRAM 초과 경고 메시지만 출력하고 다운로드 및 서빙 개설을 강제 진행함.

---

### Scenario 3: 단위 테스트 수트 실행

1. **실행 명령**:
   ```bash
   uv run pytest tests/unit/test_benchmark_context.py tests/unit/test_model_downloader.py
   ```
2. **기대 결과**:
   - VRAM 사전 검증 및 스킵 단정 테스트 케이스 100% PASS 통과.
