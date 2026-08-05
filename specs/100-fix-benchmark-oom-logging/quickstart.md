# Quickstart Validation Guide: 벤치마크 OOM 진단 및 실시간 로그 영구 저장 개선 (100-fix-benchmark-oom-logging)

## Prerequisites

- NVIDIA GPU 및 CUDA 가속 환경
- 가상환경 및 패키지 툴: `uv`
- 로그 경로: `logs/benchmark.log`, `logs/error.log`

---

## Scenario 1: 실시간 백엔드 로그 영구 저장 및 플러시 검증

```bash
# 1. 기존 로그 백업 및 제거
rm -f logs/benchmark.log

# 2. 강제 실측 벤치마크 파이프라인 구동
uv run python scripts/benchmark_context_window.py --force-benchmark

# 3. 벤치마크 로그 생성 및 서브프로세스 표준 출력 기록 검증
test -f logs/benchmark.log && echo "✓ logs/benchmark.log 파일 생성 확인"
grep -q "llama_model_loader" logs/benchmark.log && echo "✓ 백엔드 서브프로세스 출력 영구 저장 확인"
```

---

## Scenario 2: 동적 VRAM 예산 산출 및 타임아웃 오탐 방지 검증

```bash
# 1. 단일 모델 정밀 이진 탐색 검증
uv run python scripts/benchmark_context_window.py --fine-grained --model qwen3.5-4b --json

# 2. 프로파일 결과 json 저장 확인 및 failure_reason 필드 존재 확인
grep -q "qwen3.5-4b" config/model_context_profiles.json && echo "✓ 동적 프로파일 저장 완료"
```

---

## Scenario 3: 원스톱 `setup.sh --force-benchmark` 엔드투엔드 검증

```bash
# 1. setup.sh 원스톱 파이프라인 수치 검증
./setup.sh --force-benchmark

# 2. 전체 회귀 테스트 통과 검증
uv run pytest tests/unit/test_benchmark_context_window.py
```
