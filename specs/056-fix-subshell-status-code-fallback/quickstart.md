# Quickstart Validation Guide: Fast-Track 휠 검증 서브쉘 종료 코드 캡처 구문 수정 및 C++ 소스 재컴파일 Fallback 정상 전이 보장 (056-fix-subshell-status-code-fallback)

## Validation Scenario 1: Subshell Exit Code Capture & Fallback Test (단위 테스트)

`GPU_CHECK_OUTPUT=$(...) || GPU_CHECK_STATUS=$?` 구문 및 `set -e` 환경에서 exit code 2 캡처를 검증합니다.

```bash
# 1. 서브쉘 에러 코드 캡처 단위 테스트 실행
uv run pytest tests/unit/test_seed_pack.py -k "test_setup_subshell_error_guard_and_fallback" -v
```

- **Expected Outcome**: 테스트 통과 및 `GPU_CHECK_OUTPUT=$(...) || GPU_CHECK_STATUS=$?` 구문 검증 완료.

---

## Validation Scenario 2: `start_server.sh` Fail-Fast Pre-flight Validation Test

CPU 전용 패키지가 가상환경에 주입되었을 때 `start_server.sh` 구동 시점에서 즉시 실패(Fail-Fast)함을 검증합니다.

```bash
# 1. check-preflight 실행
uv run python -m src.core.cpu_detector --check-preflight
```

- **Expected Outcome**: `passed` 여부 및 `llama-cpp-python` CUDA 가속 상태 정확 출력.

---

## Validation Scenario 3: Real Integration & Regression Test Suite

전체 통합 및 회귀 테스트 수트를 구동합니다.

```bash
# 전체 회귀 테스트 실행
uv run pytest tests/unit tests/integration -v
```

- **Expected Outcome**: 모든 테스트 100% Green 통과.
