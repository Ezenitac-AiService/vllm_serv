# Research: Fast-Track 휠 검증 서브쉘 종료 코드 캡처 구문 수정 및 C++ 소스 재컴파일 Fallback 정상 전이 보장 (056-fix-subshell-status-code-fallback)

## Phase 0: Research & Technical Investigation

### Research Item 1: Bash `set -e` 환경에서 서브쉘 종료 코드(`$?`) 정확한 캡처 패턴

- **Problem Statement**:
  기존 `GPU_CHECK_OUTPUT=$(uv run python -c "..." 2>&1 || true)` 구문은 내부 파이썬 스크립트가 non-zero exit code (예: exit code 2 `GPU_OFFLOAD_FALSE`)를 반환할 때 `|| true`로 인해 변수 할당문 전체의 종료 코드가 `0`으로 평가됨. 이로 인해 직후 `GPU_CHECK_STATUS=$?`가 항상 `0`이 되어 휠 오프로드 성공으로 오탐함.

- **Decision & Rationale**:
  - `GPU_CHECK_OUTPUT=$(uv run python -c "..." 2>&1) || GPU_CHECK_STATUS=$?` 구문을 사용함.
  - Bash의 command substitution 문법 `VAR=$(cmd) || STATUS=$?` 형태는:
    1. `cmd`가 exit 0 성공 시: `||` 이후 조건문이 평가되지 않으므로 `$STATUS`는 `0`으로 유지(또는 이전에 0 초기화).
    2. `cmd`가 exit non-zero (예: 2, 132) 실패 시: `||` 절로 넘어와 `$STATUS`에 `cmd`의 실제 exit code가 즉시 할당됨.
    3. `set -e` 모드에서도 변수 할당 구문이 `||` 숏서킷 연산자와 결합되어 있으므로 셸 스크립트 전체가 비정상 종료(abort)되지 않고 안전하게 실행을 계속함.

- **Alternatives Considered**:
  - `GPU_CHECK_OUTPUT=$(uv run python -c "..." 2>&1 || echo "FAIL_OFFLOAD")`: exit code 파싱 대신 문자열 패턴 매칭만 사용하는 방법 -> `SIGILL`(132)이나 파이썬 런타임 세그폴트 시 exit code 구분이 불명확해지므로 기각.
  - `set +e`로 잠시 끈 후 실행: `set +e` 구간 작성 시 다른 구문에서 예외를 놓칠 수 있으며 코드 가독성이 떨어짐 -> 기각.

---

### Research Item 2: 사전 빌드 휠 검증 실패 시 기존 가상환경 패키지 자동 정리(Clean) 방식

- **Problem Statement**:
  Tier 1/Tier 3에서 사전 빌드 휠을 `uv pip install`로 설치한 후 GPU 오프로드 검증에 실패하여 Tier 4 C++ 소스 재컴파일로 Fallback할 때, 가상환경 내에 불일치 휠 패키지 잔재가 남아 재컴파일 캐시 충돌이나 아티팩트 오염을 유발할 수 있음.

- **Decision & Rationale**:
  - Tier 4 C++ 소스 재컴파일 진입 직전에 `uv pip uninstall llama-cpp-python` 명령을 명시적으로 실행함 (명확화 세션 Option A 결정을 반영).
  - 이를 통해 기존 사전 휠 아티팩트를 깔끔히 제거한 후 C++ 소스 재컴파일(`CMAKE_ARGS="$DETECTED_CMAKE_ARGS" uv pip install "llama-cpp-python[server]" --no-binary llama-cpp-python`)을 실행하므로 100% 결함 없는 빌드 환경이 확보됨.

---

### Research Item 3: `start_server.sh` 구동 시점의 2중 사전 점검(Pre-flight Check) 보강

- **Problem Statement**:
  기존 `src/core/cpu_detector.py`의 `check_hardware_preflight()`는 `nvidia-smi` 및 `nvcc` 존재 여부만 체크하여, 파이썬 가상환경(`.venv`)의 `llama-cpp-python` 패키지가 실제 CUDA 가속 기능을 포함하고 있는지 점검하지 않음. 이로 인해 CPU 전용 패키지가 설치되어 있어도 `start_server.sh`가 통과하여 구동되는 맹점이 존재함.

- **Decision & Rationale**:
  - `check_hardware_preflight()` 함수 내에 `llama_cpp.llama_supports_gpu_offload()` 검증 단계를 추가함.
  - 검증 실패 시 `passed: False`, `error_message: "❌ [Pre-flight Fail] llama-cpp-python 패키지가 CUDA GPU 가속을 지원하지 않습니다 (CPU 전용 모드)."`를 반환하여 `start_server.sh` 구동 시점에서 명시적 에러 메시지와 함께 즉시 실패(Fail-Fast)하여 데몬 생성을 차단함.
