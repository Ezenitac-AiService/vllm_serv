# Quickstart Validation Guide: 동적 모델-KV 메모리 기반 벤치마크 탐색 구간 자동 산정 (Dynamic Benchmark Range)

**Feature**: `107-dynamic-benchmark-range`
**Date**: 2026-08-07

## Prerequisites

- NVIDIA GPU & Driver (`nvidia-smi` 감지 가능 환경)
- Active Virtualenv (`uv run`)

## Validation Scenarios

### Scenario 1: `gemma4-e2b` 동적 탐색 상한선 16K 자동 확장 검증

```bash
# 1. 서빙 서버 종료 후 100% VRAM 해제 검증
./stop_server.sh

# 2. gemma4-e2b 정밀 이진 탐색 실행 (11GB VRAM 환경에서 상한선이 [4096, 16384]로 자동 확장되는지 확인)
uv run python scripts/benchmark_context_window.py --model gemma4-e2b --fine-grained
```

**Expected Outcome**:
- `[Binary Search GPU Load] 🚀 실측 GPU 프로세스 스폰 이진 탐색 개시 (모델=gemma4-e2b, Base VRAM=3759MB, 구간=[4096, 16384])...` 로그 출력.
- 탐색 상한선 `high`가 4096 상수에 제약받지 않고 16384(또는 모델 max)까지 동적 설정됨.

---

### Scenario 2: `./stop_server.sh` VRAM 완전 해제 및 `llama_cpp.server` 사살 검증

```bash
# 백그라운드 서버 구동 후 stop_server.sh 실행
./stop_server.sh

# 잔여 프로세스 및 VRAM 실측 확인
pgrep -f "llama_cpp.server" || echo "✓ 잔여 프로세스 0건"
nvidia-smi --query-gpu=memory.used --format=csv,noheader
```

**Expected Outcome**:
- `pgrep -f "llama_cpp.server"` 결과가 빈 문자열(0건).
- NVML VRAM 사용량이 500MB 미만으로 100% 해제 완료됨.

---

### Scenario 3: 단위 및 통합 테스트 회귀 검증

```bash
uv run pytest tests/unit/test_gpu_detector.py tests/unit/test_benchmark_context_window.py tests/unit/test_process_manager_health.py tests/unit/test_process_manager_cleanup.py
```

**Expected Outcome**:
- 전체 단위 테스트 수트 100% PASS (0 failures).
