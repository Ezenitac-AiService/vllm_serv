# Research: 이관 서버 환경 setup.sh Fast-Track 검증 예외 안전성 및 소스 컴파일 Fallback 보장 (055-fix-migration-setup-fallback)

**Feature Branch**: `055-fix-migration-setup-fallback`
**Date**: 2026-07-31

---

## Technical Decisions & Research Summary

### 1. Fast-Track 사전 휠 GPU 가속 검증 서브쉘 `set -e` 에러 가드 (`|| true`)

- **Decision**: `scripts/setup.sh` 내 Fast-Track 사전 빌드 휠 검증 서브쉘 호출 시 `GPU_CHECK_OUTPUT=$(uv run python -c "..." 2>&1 || true)` 구문을 적용하고, 서브쉘 실행 직후 `$GPU_CHECK_OUTPUT` 내용과 파싱 상태를 명시적으로 평가하여 스크립트 강제 종료(exit)를 차단.
- **Rationale**:
  - `setup.sh` 상단에 `set -eo pipefail` 구문이 활성화되어 있으므로, 캡처 구문 `VAR=$(cmd 2>&1)` 실행 시 `cmd`가 0이 아닌 에러 코드를 반환하면 bash는 `GPU_CHECK_STATUS=$?` 라인에 도달하기 전 스크립트를 즉시 중단함.
  - `|| true` 가드를 적용하면 `set -e` 상태에서도 스크립트 중단 없이 트레이스백을 캡처하고 원인(SIGILL, GPU_OFFLOAD_FALSE, Shared Lib Missing 등)을 분석하여 소스 재컴파일 파이프라인으로 안전하게 전이될 수 있음.
- **Alternatives Considered**:
  - `set +e` 임시 해제: 스크립트 전체의 에러 감지 능력을 떨어뜨리므로 서브쉘 할당 단위 `|| true` 가드가 훨씬 안전함.

---

### 2. 결정론적 4단계 우선순위 휠 감지 & 3중 정합성 검증 체계 (Priority Hierarchy)

- **Decision**: `setup.sh`의 휠 감지 및 복원 서순을 아래 4단계 우선순위 계층으로 고도화하고, 각 단계마다 3중 정합성 검증(CPU SIMD 명령어, CUDA 가속 `llama_supports_gpu_offload()`, Compute Capability 매칭)을 수행.
  1. **우선순위 1 (`--wheel-path <PATH>`)**: CLI 인자로 명시 지정한 커스텀 휠 경로 최우선 검증 및 설치.
  2. **우선순위 2 (현지 가상환경 `.venv` 캐시)**: 기존 `.venv` 내 `llama-cpp-python`이 존재하고 3중 검증을 100% 통과하면 재설치 없이 0.05초 고속 리턴.
  3. **우선순위 3 (Seed Pack 번들 휠 `wheels/legacy_i7_930/*.whl`)**: `.venv` 미설치 또는 검증 실패 시 번들 휠을 3중 검증 후 0.5초 Fast-Track 복원.
  4. **우선순위 4 (동적 C++ 소스 재컴파일 Fallback)**: 사전 휠 미존재 또는 3중 검증 실패 시 `DETECTED_CMAKE_ARGS` 기반 소스 컴파일로 100% CUDA 가속 보장.
- **Rationale**: 타겟 레거시 서버에 이미 올바른 휠이 존재하거나 사용자가 명시한 휠이 있는 경우 컴파일 시간을 최소화하면서도, 불일치 휠 유입 시 CPU 오프로딩 저하나 SIGILL 크래시를 100% 막아냄.

---

### 3. 루트 디렉터리 제어 심볼릭 링크 확정 생성

- **Decision**: `setup.sh` 완결 단계(Step 4)에서 `./start_server.sh`, `./stop_server.sh`, `./status_server.sh` 심볼릭 링크 생성을 보장하며, `start_server.sh` 구동 시 사전 체크 및 헬스점검 루틴을 내장함.
- **Rationale**: 이관 타겟 서버에서 사용자가 루트 디렉터리에서 바로 제어 명령어(`./start_server.sh`)를 사용할 수 있도록 실행 경로 보장.
