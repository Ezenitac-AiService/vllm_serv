# Research & Technical Decisions: setup.sh 강제 빌드 옵션(--force-build) 및 benchmark_context_window NameError 크래시 수정

**Feature**: `specs/114-fix-setup-force-build-and-benchmark-crash`  
**Date**: 2026-08-08  

## Executive Summary

마이그레이션 타겟 서버에서 발생할 수 있는 2가지 핵심 결함(`benchmark_context_window.py` `NameError` 크래시 및 `setup.sh` 강제 재설치 우회 오판)의 기술적 원인 분석 및 해결 방안을 결정하였습니다.

---

## 1. Technical Decisions

### Decision 1: benchmark_context_window() 내 usable_vram & remaining_kv_budget 명시적 산출
- **Context**: `scripts/benchmark_context_window.py`의 `benchmark_context_window()` 함수(Line 267)에서 `usable_kv_budget_mb=remaining_kv_budget` 인자를 전달하지만 `remaining_kv_budget` 변수가 미선언 상태여서 `NameError` 크래시가 발생함.
- **Decision**: `benchmark_context_window()` 진입부에서 GPU VRAM 용량을 탐지하여:
  ```python
  usable_vram = max(0, total_vram - 1024)
  remaining_kv_budget = max(0, usable_vram - base_vram)
  ```
  를 명시적으로 계산한 후 `calculate_max_allocatable_n_ctx` 함수에 안전하게 전달합니다.
- **Rationale**: VRAM 연산 변수를 사전 보장하여 스크립트 실행 중 무조건적인 런타임 예외를 차단합니다.
- **Alternatives Considered**: 하드코딩된 예산 값 전달 (거부 이유: 동적 GPU VRAM 용량 반응 실패).

### Decision 2: setup.sh CLI 옵션에 --force-build 추가 및 FORCE_BUILD 플래그 연동
- **Context**: 타겟 서버에서 기존 가상환경의 결함 패키지나 CPU 전용 패키지를 강제로 지우고 CUDA C++ 재컴파일을 원해도 스킵되는 문제.
- **Decision**: `scripts/setup.sh` 옵션 파싱 루프에 `--force-build` 플래그를 추가하고 `FORCE_BUILD=1`을 설정합니다.
- **Rationale**: 사용자가 명시적으로 빌드를 요청할 때 기존 Fast-Track 스킵 로직을 우회할 표준 제어 수단 제공.

### Decision 3: FORCE_BUILD=1 또는 --wheel-path 설정 시 Fast-Track 스킵 및 --no-cache-dir 강제
- **Context**: `--wheel-path`를 넘겨주더라도 `setup.sh` 1단계의 캐시 검증(`verify_wheel_binary.py`)이 통과해버리면 `INSTALLED_VIA_FAST_TRACK=1`로 설정되어 커스텀 휠 재설치가 무시됨.
- **Decision**:
  - `FORCE_BUILD=1` 또는 `WHEEL_PATH`가 존재하는 경우, Fast-Track 휠 검증 단계를 명시적으로 스킵 (`INSTALLED_VIA_FAST_TRACK=0`).
  - `--wheel-path` 지정 시: `uv pip install "$WHEEL_PATH" --force-reinstall --no-index` 강제 구동.
  - `--force-build` 지정 시: `uv pip install --no-cache-dir --force-reinstall "llama-cpp-python[server]" --no-binary llama-cpp-python` 구동.
- **Rationale**: 사용자 지시 옵션이 기존 캐시 상태보다 최우선시되어 어떠한 마이그레이션 상태에서도 CUDA 휠 강제 생성이 보장됨.

---

## 2. Risk & Impact Analysis

| Risk | Mitigation |
|------|------------|
| C++ 소스 재컴파일 시 수 분 소요 | `--force-build`는 사용자의 명시적 의도일 때만 구동되므로 기본 구동 속도에 영향 없음 |
| `--wheel-path` 잘못된 경로 지정 | `setup.sh` 입력 검증 단계에서 휠 파일 존재 여부(`[ -f "$WHEEL_PATH" ]`) 즉시 확인 후 실패 시 명확한 에러 출력 |
