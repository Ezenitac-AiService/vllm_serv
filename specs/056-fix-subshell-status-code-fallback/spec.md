# Feature Specification: Fast-Track 휠 검증 서브쉘 종료 코드 캡처 구문 수정 및 C++ 소스 재컴파일 Fallback 정상 전이 보장 (056-fix-subshell-status-code-fallback)

**Feature Branch**: `056-fix-subshell-status-code-fallback`

**Created**: 2026-07-31

**Status**: Draft

**Input**: Migration log analysis from `/home/dev/storage/vllm_serv/log.txt`

## Clarifications

### Session 2026-07-31
- Q: 사전 빌드 휠 가속 검증 실패 시 기존 가상환경 패키지 자동 정리(Clean) 여부 → A: Option A (Tier 4 C++ 재컴파일 진입 전 `uv pip uninstall llama-cpp-python`으로 실패한 사전 휠을 깨끗이 정리 후 재컴파일 진행)

---

## Technical Context & Scope Analysis (기술적 맥락 및 로그 분석)

서비스 플랫폼 타겟 서버(Intel i7-930 + GTX 1070)에 이관 후 `./setup.sh`를 재실행한 실제 로그(`log.txt`) 분석 결과 다음과 같은 치명적인 서브쉘 종료 코드 오탐 결함이 발견되었습니다:

1. **서브쉘 종료 코드(`$?`) 덮어쓰기 오탐 버그 (Root Cause)**:
   - `scripts/setup.sh` 218행: `GPU_CHECK_OUTPUT=$(uv run python -c "..." 2>&1 || true)` 구문 실행 시, 내부 `uv run python`이 exit code 2 (GPU_OFFLOAD_FALSE)를 반환하더라도 뒤따르는 `|| true`에 의해 변수 할당문 전체의 종료 코드가 `0`으로 평가되었습니다.
   - 그 결과 직후 줄의 `GPU_CHECK_STATUS=$?`가 항상 `0`으로 설정되어, `setup.sh`는 사전 빌드 휠 GPU 검증이 성공한 것으로 오탐하였습니다:
     ```text
     [SETUP INFO] ✓ 사전 빌드 휠 Fast-Track 설치 및 CUDA GPU 가속 활성화 확인 완료 (C++ 소스 재컴파일 스킵됨)
     ```
   - 이로 인해 사전 휠이 실제로 CUDA 오프로딩 불가능 상태(`llama-cpp-python GPU: ✗ CPU 전용 모드`)임에도 C++ 소스 재컴파일 파이프라인으로 Fallback하지 못하고 설치가 완료 처리되었습니다.

2. **서버 구동 후 CUDA 오프로딩 미기동 및 PID 불일치**:
   - `setup.sh`가 오탐으로 인해 C++ 소스 재컴파일을 수행하지 않고 끝난 후 `./start_server.sh` 및 `./status_server.sh`를 구동했을 때, `llama-cpp-python`이 CPU 전용 상태로 잔류하여 `llama-server` 프로세스가 VRAM 오프로딩에 실패하였습니다 (`PID: null`, `GPU 컴퓨트 프로세스 없음`).

본 명세는 `setup.sh` 내 서브쉘 변수 할당 구문을 `GPU_CHECK_OUTPUT=$(uv run python -c "..." 2>&1) || GPU_CHECK_STATUS=$?` 형태로 수정하여, `set -e` 환경 하에서 스크립트 중단을 방지하면서도 실제 `uv run python`의 에러 반환 코드를 100% 캡처하여 C++ 소스 재컴파일 Fallback으로 정상 전이되도록 보장하는 것을 목적으로 합니다.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Fast-Track 검증 서브쉘 종료 코드 실측 캡처 및 C++ 소스 컴파일 Fallback 100% 보장 (Priority: P1) 🎯 MVP

사용자나 DevOps 관리자가 이관 타겟 서버에서 `./setup.sh`를 실행할 때, 번들링된 사전 빌드 휠의 CUDA 가속 검증(`llama_supports_gpu_offload()`)이 `False`를 반환하는 경우 스크립트가 성공으로 오탐하거나 도중에 튕기지 않고, 실패 원인을 명시적 경고 로그로 출력한 후 `INSTALLED_VIA_FAST_TRACK=0` 상태에서 `DETECTED_CMAKE_ARGS` 기반 C++ 소스 컴파일 파이프라인으로 100% 자동 전이됩니다.

- **서브쉘 종료 코드 정확 캡처**: `GPU_CHECK_OUTPUT=$(uv run python -c "..." 2>&1) || GPU_CHECK_STATUS=$?` 적용.
- **C++ 소스 컴파일 Fallback 100% 전이**: `GPU_CHECK_STATUS != 0` 감지 시 소스 재컴파일 수행.

**Why this priority**: 사전 휠 불일치 환경에서 CPU 전용 모드로의 오탐 방치 현상을 근본적으로 해결하는 최우선 결함 수정 과제입니다.

**Independent Test**:
1. Fast-Track 사전 휠 GPU 검증이 실패하도록 유도한 상태에서 `bash scripts/setup.sh` 실행 시, `[FAST-TRACK FAIL]` 경고가 출력되고 C++ 소스 컴파일 파이프라인으로 전이되어 100% CUDA 가속 설치가 완결되는지 확인.

---

### User Story 2 - 이관 타겟 머신에서의 100% CUDA 가속 검증 및 status_server.sh 정상 연동 (Priority: P1) 🎯 MVP

설치 및 서빙 기동 완료 후 `./status_server.sh` 실행 시 `llama-cpp-python GPU: ✓ CUDA 가속 활성` 리포트가 출력되고, `llama-server` 백엔드 프로세스 PID 및 GPU VRAM 오프로드가 정상 확인됩니다.

- **CUDA 가속 실측 검증**: `status_server.sh`에서 `GPU 컴퓨트 프로세스` 및 CUDA 가속 활성화 검증.

**Why this priority**: 이관 서버 환경에서 서빙 인프라의 정상 동작을 최종 실측 보장합니다.

**Independent Test**:
1. `./status_server.sh` 실행 결과 `llama-cpp-python GPU` 가 `✓ CUDA 가속 활성`으로 표기되는지 확인.

---

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `scripts/setup.sh` 내 서브쉘 변수 할당 시 `GPU_CHECK_OUTPUT=$(...) || GPU_CHECK_STATUS=$?` 적용으로 종료 코드 0 덮어쓰기 오탐 버그 수정 완료.
- **DoD-002**: 사전 휠 GPU 검증 실패 시 `INSTALLED_VIA_FAST_TRACK=0` 설정 및 C++ 소스 컴파일 파이프라인으로의 자동 Fallback 검증 완료.
- **DoD-003**: `./status_server.sh` 실행 시 `llama-cpp-python GPU: ✓ CUDA 가속 활성` 및 PID 상주 실측 보장.
- **DoD-004**: 단위 및 회귀 테스트 수트 pass.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `scripts/setup.sh` 내 Fast-Track 휠 GPU 가속 검증 서브쉘 실행 구문을 `GPU_CHECK_OUTPUT=$(uv run python -c "..." 2>&1) || GPU_CHECK_STATUS=$?`로 수정하여 `set -e` 구문 하에서도 스크립트 중단을 방지함과 동시에 `uv run python`의 실제 에러 반환 코드를 `GPU_CHECK_STATUS` 변수에 정확히 캡처해야 한다.
- **FR-002**: `GPU_CHECK_STATUS`가 0이 아닌 경우 `setup.sh`는 `[FAST-TRACK FAIL]` 경고와 트레이스백을 로그에 출력하고, `INSTALLED_VIA_FAST_TRACK=0`을 유지하며 Tier 4 C++ 재컴파일 진입 전 `uv pip uninstall llama-cpp-python`을 수행하여 실패한 사전 휠을 언인스톨 후 `DETECTED_CMAKE_ARGS` 기반 C++ 소스 재컴파일 파이프라인으로 100% 자동 전이되어 CUDA GPU 가속을 완성해야 한다.
- **FR-003**: 헌법 v1.6.0에 따라 `GPU_CHECK_OUTPUT=$(...) || GPU_CHECK_STATUS=$?` 서브쉘 구문 및 에러 코드 캡처 동작을 검증하는 단위 테스트(`tests/unit/test_seed_pack.py` 내 추가)를 작성하고 Green 통과를 보장해야 한다.
- **FR-004**: `src/core/cpu_detector.py` 내 `check_hardware_preflight()` 함수 및 `start_server.sh` 사전 점검 파이프라인에 `llama_cpp.llama_supports_gpu_offload()` 패키지 CUDA 가속 검증을 추가하여, `.venv` 내 `llama-cpp-python` 패키지가 CPU 전용으로 잘못 설치된 경우 `start_server.sh` 구동 시점에서 명시적 에러 메시지와 함께 즉시 실패(fail-fast)하고 데몬 생성을 차단해야 한다.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 이관 타겟 레거시 서버에서 사전 휠 오프로드 실패 시 C++ 소스 컴파일 파이프라인 자동 전이 및 완성 성공률 **100%**.
- **SC-002**: `./status_server.sh` 실행 시 `llama-cpp-python GPU: ✓ CUDA 가속 활성` 확인율 **100%**.
- **SC-003**: 관련 단위 및 회귀 테스트 수트 100% Pass.

---

## Assumptions

- bash 환경에서 `VAR=$(cmd 2>&1) || STATUS=$?` 구문은 `set -e`가 활성화되어 있어도 `cmd`가 실패할 때 스크립트를 중단하지 않고 `STATUS`에 `cmd`의 실제 exit code를 저장합니다.
