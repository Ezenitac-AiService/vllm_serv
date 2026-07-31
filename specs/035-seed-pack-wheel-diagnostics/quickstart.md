# Quickstart Guide: Seed Pack Wheel Validation & Setup Failure Diagnostics

## Overview

본 가이드는 시드 팩 사전 빌드 휠 바이너리 검증 및 `setup.sh` 상세 진단 기능의 실행 시나리오를 안내합니다.

## Runnable Validation Scenarios

### Scenario 1: 사전 빌드 휠 파이썬 전용 바이너리 검증 테스트

`wheels/legacy_i7_930/*.whl` 내 모든 `.so` 아티팩트에 AVX 명령어가 전혀 수록되지 않았는지 검증합니다.

```bash
uv run python scripts/verify_wheel_binary.py wheels/legacy_i7_930/llama_cpp_python-0.3.34-py3-none-linux_x86_64.whl
```

### Scenario 2: 시드 팩 아카이브 조건부 휠 재컴파일 실행

기존 휠 검증 통과 시 컴파일 스킵(0초), 오염 휠 감지 시 자동 삭제 및 재컴파일 동작을 확인합니다.

```bash
./scripts/make_seed_pack.sh
```

### Scenario 3: `setup.sh` Fast-Track 진단 에러 출력 검증

`setup.sh` 구동 시 사전 빌드 휠 검증 실패 상황을 모의하여 에러 은폐(`2>/dev/null`) 없이 상세 진단 로그가 표출되는지 테스트합니다.

```bash
uv run pytest tests/unit/test_shell_scripts.py -v
```

## Expected Outcomes

- 정상 휠 감지 시 C++ 소스 재컴파일을 0초 만에 스킵하고 기존 휠 즉시 패키징.
- AVX 오염 휠 감지 시 기존 휠을 자동 삭제(Clean) 후 `-DGGML_AVX=OFF` 인자로 안전한 휠 새로 빌드.
- `setup.sh`에서 Fast-Track 검증 실패 시 구조화된 1줄 핵심 원인 로그 및 상세 Traceback 100% 출력.
