# Feature Specification: 이관 서버 환경 setup.sh Fast-Track 검증 예외 안전성 및 소스 컴파일 Fallback 보장 (055-fix-migration-setup-fallback)

**Feature Branch**: `055-fix-migration-setup-fallback`

**Created**: 2026-07-31

**Status**: Draft

**Input**: User request & migration log analysis from `/home/dev/storage/vllm_serv/log.txt`

---

## Technical Context & Scope Analysis (기술적 맥락 및 로그 분석)

서비스 플랫폼 타겟 서버(Intel i7-930 + GTX 1070)에 `vllm_serv_seed.tar.gz` 아카이브를 마이그레이션한 후 `./setup.sh` 및 `./start_server.sh`를 구동한 실제 로그(`log.txt`) 분석 결과 다음 3가지 핵심 취약점 및 결함이 확인되었습니다:

1. **`set -e` 파이프라인 강제 중단 버그 (Fatal Bug)**:
   - `scripts/setup.sh` 196행: `GPU_CHECK_OUTPUT=$(uv run python -c "..." 2>&1)` 실행 시 Fast-Track 사전 빌드 휠의 CUDA 가속 검증이 `False`를 반환할 때, `set -e` 정책에 의해 `uv run python`의 에러 반환 코드(code 2)가 검출되면서 `setup.sh` 전체 프로세스가 Step 2 (64행)에서 즉시 강제 종료되었습니다.
   - 이로 인해 C++ 소스 재컴파일 파이프라인(`CMAKE_ARGS="$DETECTED_CMAKE_ARGS" uv pip install ...`)으로의 Fallback 분기가 실행되지 못했습니다.

2. **루트 디렉터리 심볼릭 링크 생성 미도달**:
   - `setup.sh`가 Step 2에서 비정상 중단됨에 따라 Step 4(루트 제어 심볼릭 링크 `./start_server.sh`, `./stop_server.sh`, `./status_server.sh` 생성) 및 Step 4.6(시드 DB 초기화) 섹션에 도달하지 못했습니다.
   - 그 결과 사용자가 `./start_server.sh` 구동 시 `bash: ./start_server.sh: No such file or directory` 에러가 발생했습니다.

3. **CUDA 가속 미활성화 상태 방치**:
   - 사용자가 직접 `/home/dev/vllm_serv/scripts/start_server.sh`를 개별 실행하였으나, `setup.sh`에서 소스 컴파일 Fallback이 수행되지 않아 `llama-cpp-python`이 CUDA 오프로딩 불가능 상태(`llama-cpp-python GPU: ✗ CPU 전용 모드`)로 잔류하여 `llama-server` 백엔드가 기동되지 못했습니다 (`PID: null`, `GPU 컴퓨트 프로세스 없음`).

본 명세는 이러한 `setup.sh` 파이프라인 서브쉘 예외 처리 버그를 근본적으로 수정하여, 사전 휠 검증 실패 시에도 안전하게 소스 컴파일 파이프라인으로 전이되어 100% CUDA 가속 서빙과 제어 스크립트 생성을 보장하는 것을 목적으로 합니다.

---

## Clarifications

### Session 2026-07-31
- **Q: 서비스 플랫폼 현지 빌드 바이너리/휠 활용 및 시드 팩 동기화 방식** → **A: Option A-C 혼합 고도화 3단계 휠/바이너리 복원 파이프라인 적용**
  - **1단계 (Option C - 가상환경 현지 캐시 재사용)**: `.venv` 내 기존 `llama-cpp-python`이 존재하고 `llama_supports_gpu_offload()`가 `True`인 경우 소스 컴파일 및 휠 재설치를 스킵하고 기존 환경을 유지.
  - **2단계 (Option A & B - 사전 빌드 휠 & 커스텀 경로 `--wheel-path` Fast-Track)**: `.venv` 미설치 또는 GPU 검증 실패 시 `--wheel-path` 지정 경로 및 `wheels/legacy_i7_930/` 디렉터리 내 현지 빌드 휠을 감지하여 0.5초 이내 Fast-Track 복원.
  - **3단계 (안전한 C++ 소스 컴파일 Fallback)**: 서브쉘 `set -e` 에러 가드(`|| true`) 적용 하에 사전 휠 검증 실패 시에만 `DETECTED_CMAKE_ARGS` 기반 동적 C++ 소스 컴파일 파이프라인으로 전이.
- **Q: 발견된 기존 바이너리/휠의 플랫폼 상태 정보 정합성 검증 추가** → **A: 실시간 하드웨어 감지 리포트(`cpu_detector`) 기반 3중 검증 체계 구현**
  - 기존/지정 바이너리(휠) 감지 시 단순 임포트 외에 **(1) CPU SIMD 명령어 호환성(AVX/AVX2/FMA 유입 차단), (2) CUDA GPU 가속 활성화(`llama_supports_gpu_offload()`), (3) Compute Capability (예: `sm_61`) 플랫폼 상태 매칭** 3중 검증을 필수 수행하며, 미부합 시 즉시 파기(Clean) 후 소스 재컴파일로 자동 전환.
- **Q: 기존 바이너리/휠 감지 및 복원 서순(Priority Hierarchy) 최적화 방안** → **A: 4단계 결정론적 우선순위 휠 감지 체계 확정**
  - **우선순위 1 (`--wheel-path <PATH>`)**: 사용자가 CLI 인자로 명시 전달한 커스텀 휠 경로를 최우선 3중 검증 및 복원.
  - **우선순위 2 (현지 가상환경 `.venv` 캐시)**: 이미 `.venv` 내 설치된 `llama-cpp-python`이 3중 검증을 통과하는 경우 소스 재컴파일 및 휠 설치를 스킵하고 0.05초 고속 리턴.
  - **우선순위 3 (Seed Pack 수록 사전 빌드 휠 번들 `wheels/`)**: `.venv` 미설치/검증 실패 시 `wheels/` 내 번들 휠을 3중 검증 후 0.5초 Fast-Track 복원.
  - **우선순위 4 (동적 C++ 소스 컴파일 Fallback)**: 상기 사전 휠이 없거나 3중 검증 실패 시 `DETECTED_CMAKE_ARGS` 기반 동적 C++ 소스 컴파일로 100% CUDA 가속 보장.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Fast-Track 휠 검증 서브쉘 `set -e` 비정상 종료 방지 및 안전한 C++ 소스 컴파일 Fallback 보장 (Priority: P1) 🎯 MVP

사용자나 DevOps 관리자가 이관 타겟 서버에서 `./setup.sh`를 실행할 때, 번들링된 사전 빌드 휠이 타겟 서버의 CUDA/공유 라이브러리 환경과 일치하지 않더라도 `setup.sh` 스크립트가 도중에 비정상 중단(exit)되지 않고 에러 원인을 로그에 기록한 후 `DETECTED_CMAKE_ARGS` 기반의 C++ 소스 컴파일 파이프라인으로 자동 전이되어 100% CUDA 가속 빌드를 완료합니다.

- **서브쉘 예외 안전 가드 적용**: `GPU_CHECK_OUTPUT=$(uv run python -c "..." 2>&1 || true)` 구문으로 `set -e`에 의한 스크립트 튕김 차단.
- **C++ 소스 컴파일 Fallback 보장**: 사전 휠 GPU 검증 실패 시 `CMAKE_ARGS="$DETECTED_CMAKE_ARGS" uv pip install ...` 자동 수행 및 CUDA 가속 활성화(`assert fn()`) 확인.

**Why this priority**: 신규 또는 이관 서버 환경에서 설치 실패 및 CPU 전용 모드로의 저하를 완벽히 차단하는 최우선 결함 수정 과제입니다.

**Independent Test**:
1. Fast-Track 사전 휠 GPU 검증이 실패하도록 유도한 상태에서 `bash scripts/setup.sh` 실행 시, 스크립트가 튕기지 않고 `[FAST-TRACK FAIL]` 경고 후 C++ 소스 컴파일 파이프라인으로 자동 전환되어 정상 완결되는지 확인.

---

### User Story 2 - `setup.sh` 완결성 및 루트 제어 심볼릭 링크(`./start_server.sh` 등) 확정 생성 (Priority: P1) 🎯 MVP

사용자가 `./setup.sh` 실행 완료 후 레포지토리 루트 디렉터리에서 `./start_server.sh`, `./stop_server.sh`, `./status_server.sh` 명령어 실행 시 `No such file or directory` 에러 없이 즉시 구동 및 상태 조회가 가능합니다.

- **루트 심볼릭 링크 100% 생성**: `start_server.sh`, `stop_server.sh`, `status_server.sh` 링크 보장.

**Why this priority**: 사용자 경험(UX) 및 서빙 제어 스크립트 접근성을 완전히 보장합니다.

**Independent Test**:
1. `./setup.sh` 구동 완료 후 레포지토리 루트에서 `./start_server.sh` 및 `./status_server.sh` 파일이 심볼릭 링크로 정상 연결되어 실행 가능한지 확인.

---

### User Story 3 - 이관 타겟 머신에서의 100% CUDA 가속 검증 및 회귀 테스트 수트 강화 (Priority: P2)

설치 및 서빙 기동 완료 후 `./status_server.sh` 실행 시 `llama-cpp-python GPU: ✓ CUDA 가속 활성` 리포트가 정상 출력되고, `llama-server` 백엔드 프로세스 PID 및 GPU VRAM 오프로드가 정상 확인됩니다.

- **CUDA 가속 실측 검증**: `status_server.sh`에서 `GPU 컴퓨트 프로세스` 수록 검증.

**Why this priority**: 이관 서버 환경에서 CPU 전용 오프로딩 저하를 방지하고 GPU 가속 서빙을 검증합니다.

**Independent Test**:
1. `./status_server.sh` 실행 결과 `llama-cpp-python GPU` 가 `✓ CUDA 가속 활성`으로 표기되는지 실측 확인.

---

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `scripts/setup.sh` 내 Fast-Track 휠 GPU 검증 서브쉘의 `set -e` 중단 버그 수정 (`|| true` 적용) 완료.
- **DoD-002**: 사전 휠 GPU 검증 실패 시 C++ 소스 컴파일 파이프라인으로의 자동 Fallback 및 CUDA 가속 활성화 검증 완료.
- **DoD-003**: `./setup.sh` 완결 후 루트 디렉터리 `./start_server.sh`, `./stop_server.sh`, `./status_server.sh` 심볼릭 링크 생성 100% 확인.
- **DoD-004**: 전체 회귀 테스트 수트 및 서브쉘 방어 테스트 pass.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `scripts/setup.sh` 내 Fast-Track 휠 GPU 가속 검증 변수 할당 시 `GPU_CHECK_OUTPUT=$(uv run python -c "..." 2>&1 || true)` 파이프라인 가드를 적용하여 `set -e` 구문 조건 하에서도 `uv run python`의 0이 아닌 종료 코드가 `setup.sh` 전체 프로세스를 중단시키지 않아야 한다.
- **FR-002**: Fast-Track 휠 GPU 검증 실패 시 `setup.sh`는 명시적 경고 로그(`[FAST-TRACK FAIL]`)와 실패 원인 트레이스백을 출력한 후, 감지된 하드웨어 프로필(`DETECTED_CMAKE_ARGS`) 기반의 C++ 소스 컴파일 파이프라인으로 안전하게 Fallback하여 GPU 가속(`assert fn()`)을 완성해야 한다.
- **FR-003**: `scripts/setup.sh` 완결 단계에서 루트 심볼릭 링크(`./start_server.sh`, `./stop_server.sh`, `./status_server.sh`)가 반드시 생성되어 사용자의 제어 스크립트 실행 경로를 100% 보장해야 한다.
- **FR-004**: 서비스 플랫폼 현지 빌드 바이너리/휠 활용을 위해 `setup.sh` 및 `make_seed_pack.sh`에 `--wheel-path <PATH>` 지정 옵션을 지원하고, 1단계(.venv 가상환경 GPU 검증) -> 2단계(사전/지정 휠 Fast-Track 복원) -> 3단계(C++ 소스 컴파일 Fallback) 3단계 고도화 결합 파이프라인을 준수해야 한다.
- **FR-005**: 기존/지정 휠 또는 바이너리 감지 시 단순 존재 여부 외에 `src.core.cpu_detector` 실시간 감지 상태와 대조하여 (1) CPU SIMD 명령어 호환성(Nehalem 등 AVX 미지원 호스트 내 AVX 유입 금지), (2) CUDA GPU 가속 활성화(`llama_supports_gpu_offload()`), (3) Compute Capability 호환성 3중 정합성 검증을 수행하고, 미부합 시 즉시 재컴파일 파이프라인으로 전이해야 한다.
- **FR-006**: 헌법 v1.6.0에 따라 본 서브쉘 예외 처리, 바이너리 플랫폼 정합성 검증 및 3단계 Fallback 동작을 실측 검증하는 단위 테스트(`tests/unit/test_seed_pack.py` 내 추가)를 작성하고 Green 통과를 보장해야 한다.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 이관 타겟 레거시 서버에서 `./setup.sh` 실행 시 중간 튕김 현상 0건 및 설치 완결 성공률 **100%**.
- **SC-002**: `./start_server.sh` 및 `./status_server.sh` 실행 성공률 **100%**.
- **SC-003**: `status_server.sh` 실행 시 `llama-cpp-python GPU: ✓ CUDA 가속 활성` 확인율 **100%**.
- **SC-004**: 관련 단위 및 회귀 테스트 수트 100% Pass.

---

## Assumptions

- 이관 타겟 서버(Intel i7-930 + GTX 1070)는 NVCC 및 CUDA 드라이버 환경을 보유하고 있으며, 사전 휠 불일치 시 C++ 소스 컴파일을 수행할 수 있습니다.
- `setup.sh`의 `set -eo pipefail` 전체 정책은 유지하며, 서브쉘 변수 할당 시에만 예외 차단(`|| true`)을 적용합니다.
