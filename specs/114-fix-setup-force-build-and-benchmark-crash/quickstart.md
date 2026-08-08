# Quickstart & Integration Validation Guide: setup.sh 강제 빌드 및 benchmark_context_window 호환성 검증

**Feature**: `specs/114-fix-setup-force-build-and-benchmark-crash`  
**Date**: 2026-08-08  

## Validation Scenarios

### Scenario 1: benchmark_context_window.py NameError 크래시 검증

`scripts/benchmark_context_window.py`를 직접 구동하여 `NameError` 예외가 발생하지 않고 정상 종료되는지 실측 검증합니다.

```bash
# 1. 실행 명령
uv run python scripts/benchmark_context_window.py

# 2. 기대 결과
# - NameError: name 'remaining_kv_budget' is not defined 발생 0건
# - 성공 로그 출력: "✓ Context window profile cache saved to config/model_context_profiles.json"
```

---

### Scenario 2: setup.sh --wheel-path 강제 재설치 검증

`--wheel-path` 지정 시 Fast-Track 캐시 재사용을 스킵하고 해당 휠 패키지가 `--force-reinstall`로 직접 재설치되는지 검증합니다.

```bash
# 1. 실행 명령
./setup.sh --wheel-path wheels/legacy_i7_930/llama_cpp_python-0.3.16-cp312-cp312-linux_x86_64.whl --skip-benchmark

# 2. 기대 결과
# - Fast-Track 재사용 로그 스킵 확인
# - "✓ 지정 휠 패키지 강제 재설치 완료" 또는 동등 출력 확인
# - 최종 "✓ CUDA GPU 가속 활성화 최종 확인 완료" 검증 통과
```

---

### Scenario 3: setup.sh --force-build 강제 C++ 재컴파일 옵션 검증

`--force-build` 지정 시 uv 휠 캐시 및 사전 빌드 휠 검증을 스킵하고 `--no-cache-dir` 기반 재컴파일이 구동되는지 검증합니다.

```bash
# 1. 실행 명령
./setup.sh --force-build --skip-benchmark

# 2. 기대 결과
# - "🔥 --force-build 옵션 감지: 기존 휠 캐시 무효화 및 CUDA C++ 소스 강제 재컴파일 구동 중..." 로그 출력
# - 최종 Pre-flight check 통과
```

---

### Scenario 4: 회귀 테스트 수트 구동

```bash
uv run pytest tests/unit/test_process_manager.py tests/unit/test_seed_pack.py tests/unit/test_shell_scripts.py tests/unit/test_benchmark_context_window.py
```
