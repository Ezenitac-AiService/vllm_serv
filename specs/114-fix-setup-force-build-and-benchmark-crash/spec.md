# Feature Specification: setup.sh 강제 빌드 옵션(--force-build) 추가 및 benchmark_context_window NameError 크래시 수정 (Fix setup.sh Force Build & Benchmark Crash)

**Feature Name**: `fix-setup-force-build-and-benchmark-crash`  
**Feature Directory**: `specs/114-fix-setup-force-build-and-benchmark-crash`  
**Status**: Draft  
**Created**: 2026-08-08  

## User Value & Business Need

마이그레이션 대상 타겟 서버(예: 레거시 CPU/GPU 조합 서버)에서 `./setup.sh --wheel-path <PATH>` 또는 신규 강제 빌드 옵션 `./setup.sh --force-build`를 실행할 때, 기존 가상환경의 캐시 휠에 의해 재설치가 스킵되어 CPU 전용 모드로 남거나 `benchmark_context_window.py`의 `NameError`로 스크립트가 중단되는 결함을 완벽히 해결합니다. 이를 통해 어떤 타겟 서버 환경에서도 원스톱으로 CUDA GPU 가속 휠이 안전하게 강제 설치 및 보장되도록 만듭니다.

---

## User Stories & Acceptance Scenarios

### Story 1: setup.sh 강제 빌드(--force-build) 및 --wheel-path 재설치 강제화 (Priority: P1) 🎯 MVP

**User Role**: 타겟 플랫폼 마이그레이션 엔지니어 및 시스템 관리자  

**As a** 시스템 관리자  
**I want** `./setup.sh --force-build` 또는 `./setup.sh --wheel-path <PATH>` 옵션을 실행하면 기존 가상환경의 휠 캐시 상태와 무관하게 휠 재설치 및 C++ 재컴파일이 강제 수행되기를 원한다.  
**So that** CPU 전용 휠이 가상환경에 남아있더라도 확실하게 CUDA 가속 휠로 원스톱 강제 갱신할 수 있다.

#### Acceptance Scenarios

1. **Scenario 1.1: --force-build 옵션 작동**:
   - **Given**: 기존 가상환경에 `llama-cpp-python`이 이미 설치되어 있음
   - **When**: `./setup.sh --force-build` 실행
   - **Then**: Fast-Track 캐시 스킵을 우회하고 `--no-cache-dir` 기반으로 CUDA C++ 소스 재컴파일 또는 휠 강제 재설치가 구동된다.

2. **Scenario 1.2: --wheel-path 강제 재설치 보장**:
   - **Given**: `--wheel-path wheels/legacy_i7_930/llama_cpp_python-*.whl` 옵션 지정
   - **When**: `./setup.sh --wheel-path <PATH>` 실행
   - **Then**: 기존 `.venv` 설치 여부와 무관하게 지정한 휠 파일이 `uv pip install <PATH> --force-reinstall`로 직접 설치되고 CUDA 가속이 최종 검증된다.

---

### Story 2: benchmark_context_window.py NameError 예외 차단 (Priority: P1) 🎯 MVP

**User Role**: 자동화 벤치마크 시스템  

**As a** 자동 벤치마크 및 설정 반영 모듈  
**I want** `benchmark_context_window()` 함수 내부에서 `remaining_kv_budget` 변수가 미정의 상태로 참조되지 않기를 원한다.  
**So that** Step 2.8 벤치마크 실행 시 `NameError: name 'remaining_kv_budget' is not defined` 예외가 발생하지 않고 안전하게 동작한다.

#### Acceptance Scenarios

1. **Scenario 2.1: benchmark_context_window 함수 안전 실행**:
   - **Given**: `scripts/benchmark_context_window.py` 스크립트 실행
   - **When**: `benchmark_context_window(model_name=...)` 호출
   - **Then**: `usable_vram` 및 `remaining_kv_budget` 변수가 바르게 산출된 후 `calculate_max_allocatable_n_ctx`로 전달되어 `NameError` 없이 성공적으로 반환된다.

## Clarifications

### Session 2026-08-08

- Q: ./setup.sh --force-build 옵션 실행 시 C++ 재컴파일 및 캐시 처리 방식을 어떻게 적용할까요? → A: FORCE_BUILD=1 설정 시 --no-cache-dir 플래그를 적용하여 캐시를 무효화하고 C++ 소스 재컴파일을 강제 구동한다.

---

## Functional Requirements (FR-###)

- **FR-001**: `scripts/benchmark_context_window.py`의 `benchmark_context_window()` 함수 내부에 `usable_vram` 및 `remaining_kv_budget` 변수 산출 로직을 명시적으로 선언하여 `NameError` 예외 발생을 근본적으로 차단해야 한다.
- **FR-002**: `scripts/setup.sh`에 `--force-build` CLI 옵션을 추가하고, 파싱 시 `FORCE_BUILD=1` 플래그를 활성화해야 한다.
- **FR-003**: `scripts/setup.sh`에서 `FORCE_BUILD=1` 이거나 `--wheel-path`가 지정된 경우, 기존 캐시/Fast-Track 휠 검증을 스킵하고 `--no-cache-dir` 플래그 및 `--force-reinstall`을 적용하여 CUDA GPU 가속 패키지가 100% 강제 C++ 재컴파일 또는 휠 재설치로 갱신되도록 해야 한다.
- **FR-004**: `./setup.sh --help` 도움말 출력에 `--force-build` 옵션 설명을 명확히 수록해야 한다.

---

## Success Criteria (SC-###)

- **SC-001**: `python scripts/benchmark_context_window.py` 구동 시 `NameError` 0건 및 벤치마크 완수.
- **SC-002**: `./setup.sh --force-build` 및 `./setup.sh --wheel-path <PATH>` 구동 시 Fast-Track 캐시 오판 없이 강제 재설치가 구동되고 최종 Pre-flight check(CUDA 가속) 통과.
- **SC-003**: 전체 단위 테스트 수트(`uv run pytest tests/unit/`) 100% 통과.
