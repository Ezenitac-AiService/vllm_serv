# Feature Specification: 운영 쉘 스크립트 멀티 플랫폼 고도화

**Feature Branch**: `021-enhance-shell-scripts`

**Created**: 2026-07-30

**Status**: Draft

**Input**: User description: "작업 폴더에 보면, 시드 팩을 생성하는 쉘 파일과, 셋팅용 쉘 파일, 서버 실행, 상태 확인용 쉘 파일이 있어, 멀티 플렛폼 대응 스펙이 구현되었으니, 해당 파일들도 고도화 해야 하는거 아냐?"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - status_server.sh의 멀티 플랫폼 하드웨어 실시간 리포트 고도화 (Priority: P1)

운영자가 `./status_server.sh`를 실행할 때, 프로세스 상태 및 GPU VRAM 사용량뿐만 아니라, 현재 시스템의 CPU 감지 정보(모델명, SIMD 명령어 지원 현황), GPU Compute Capability(`sm_61`, `sm_86` 등), 그리고 적용된 타겟 플랫폼 프로필 매칭 정보를 투명하게 출력한다.

**Why this priority**: 현재 시스템이 i7 930 레거시 환경인지 최신 개발 환경인지, 그리고 빌드 플래그가 호환 모드로 동작 중인지 운영자가 한눈에 파악하기 위해 필수적이다.

**Independent Test**: `./status_server.sh` 스크립트를 실행하여 CPU SIMD 지원 현황, GPU Compute Capability, 적용된 플랫폼 프로필명이 터미널에 정상 출력되는지 확인한다.

**Acceptance Scenarios**:

1. **Given** 임의의 하드웨어 환경, **When** `./status_server.sh`를 실행하면, **Then** 프로세스 상태/포트 점유/VRAM 사용량과 함께 CPU 감지 정보(SSE4.2, AVX 등), GPU Compute Capability 코드, 매칭된 플랫폼 프로필명이 출력된다.
2. **Given** i7 930 레거시 서버, **When** `./status_server.sh`를 실행하면, **Then** `legacy-i7-930-gtx1070` 프로필과 AVX 비활성화 상태가 명시적으로 표시된다.

---

### User Story 2 - start_server.sh의 사전 하드웨어 가속 검증 및 파이프라인 고도화 (Priority: P1)

운영자가 `./start_server.sh`를 실행하여 서버 데몬을 백그라운드로 구동할 때, 백그라운드 전환 직전에 CPU/GPU 하드웨어 가속 및 빌드 환경 사전 점검(Pre-flight check)을 수행하여, 호환되지 않는 환경에서는 서버 구동을 즉시 중단(fail-fast)하고 원인을 출력한다.

**Why this priority**: 잘못된 빌드 옵션이나 GPU 미인식 상태에서 데몬이 실행되어 백그라운드에서 로그에만 에러를 남기고 비정상 종료되는 것을 사전에 방지한다.

**Independent Test**: GPU가 없거나 NVCC가 없는 환경에서 `./start_server.sh` 실행 시 데몬 생성 전에 명확한 에러와 함께 비제로 Exit 코드로 종료되는지 확인한다.

**Acceptance Scenarios**:

1. **Given** 정상 하드웨어 환경, **When** `./start_server.sh`를 실행하면, **Then** 하드웨어 사전 점검 로그가 출력되고 서버 프로세스가 정상 백그라운드로 구동된다.
2. **Given** GPU 드라이버 미인식 시스템, **When** `./start_server.sh`를 실행하면, **Then** 백그라운드 프로세스를 생성하지 않고 사전 점검 단계에서 에러 메시지를 출력하며 즉시 중단한다.

---

### User Story 3 - setup.sh의 플랫폼 자동 인지 패키징 및 가상환경 검증 강화 (Priority: P2)

운영자가 `./setup.sh`를 실행할 때, 하드웨어 자동 감지 결과를 플랫폼 프로필(`config/platform_profiles.json`)과 비교·검증하고, 필요시 알맞은 플랫폼 프로필을 사용자에게 안내하며, 동적 `CMAKE_ARGS` 빌드 파이프라인을 견고하게 수행한다.

**Why this priority**: 처음 설치 및 환경 구축 시 현재 시스템이 공식 지원되는 플랫폼 프로필과 일치하는지 파악하고 안정적인 초기 설정을 완료할 수 있다.

**Independent Test**: `./setup.sh` 실행 시 CPU/GPU 감지 리포트와 매칭되는 플랫폼 프로필명이 표시되고 `llama-cpp-python` 및 네이티브 바이너리 빌드 준비가 완벽히 수행되는지 확인한다.

**Acceptance Scenarios**:

1. **Given** i7 930 + GTX 1070 시스템, **When** `./setup.sh`를 실행하면, **Then** `legacy-i7-930-gtx1070` 프로필 매칭 결과와 `-DGGML_AVX=OFF` 계열 빌드 플래그가 전파되는 로그를 확인한다.

---

### User Story 4 - make_seed_pack.sh의 멀티 플랫폼 아카이빙 및 가이드 제공 (Priority: P3)

운영자가 타 서버 이관용 Seed Pack을 생성하기 위해 `./scripts/make_seed_pack.sh`를 실행할 때, `config/platform_profiles.json`과 같은 멀티 플랫폼 설정 파일이 아카이브에 누락 없이 포함되는지 검증하고, 이관 대상 플랫폼(예: i7 930 레거시 서버)에 맞는 맞춤형 이관 안내 안내문을 출력한다.

**Why this priority**: 다른 하드웨어 타겟으로 프로젝트를 이관할 때 필수 설정 및 가이드가 빠짐없이 전달되어 타겟 서버에서의 재설치가 매끄럽게 이뤄지도록 돕는다.

**Independent Test**: `./scripts/make_seed_pack.sh` 실행 후 생성된 아카이브 파일 내에 `config/platform_profiles.json`이 포함되어 있으며, 안내문이 멀티 플랫폼 시나리오를 설명하는지 확인한다.

**Acceptance Scenarios**:

1. **Given** Seed Pack 생성 명령 실행, **When** 아카이브 생성이 완료되면, **Then** `config/platform_profiles.json` 파일이 정상 포함되고 10MB 미만 용량을 유지하며, 타겟 플랫폼별 `setup.sh` 가이드가 출력된다.

---

### Edge Cases

- `config/platform_profiles.json` 파일이 손상되었거나 누락된 상태에서 `status_server.sh` 또는 `setup.sh`를 실행할 때 기본 폴백 정보가 표시되는가?
- GPU가 설치되어 있지만 CUDA toolkit(`nvcc`)이 없을 때 `start_server.sh` 사전 점검이 이를 감지하고 올바르게 사용자에게 조치 명령을 제시하는가?
- `make_seed_pack.sh`에서 `.tar.gz`와 `.zip` 양쪽 포맷 모두 `platform_profiles.json`을 올바르게 포함하는가?

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `status_server.sh` 실행 시 CPU 명령어 세트, GPU Compute Capability, 매칭된 플랫폼 프로필이 명확히 터미널에 리포트된다.
- **DoD-002**: `start_server.sh` 실행 시 백그라운드 구동 전 하드웨어 가속 사전 점검이 수행되며 실패 시 조기 중단된다.
- **DoD-003**: `setup.sh` 실행 시 감지된 하드웨어와 플랫폼 프로필 간 비교 검증 및 동적 CMAKE_ARGS 적용 로그가 출력된다.
- **DoD-004**: `make_seed_pack.sh` 생성 아카이브에 `config/platform_profiles.json` 설정이 포함되며 멀티 플랫폼 마이그레이션 가이드가 출력된다.
- **DoD-005**: 쉘 스크립트 고도화에 대한 단위 및 통합 테스트가 작성되고 모두 통과한다.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `status_server.sh`는 실행 시 `src.core.cpu_detector` 모듈을 활용하여 CPU 모델, SIMD 명령어 지원 현황(AVX/AVX2/F16C/FMA), GPU Compute Capability (`sm_61`, `sm_86` 등), 매칭된 플랫폼 프로필 정보를 로그로 출력해야 한다 (MUST).
- **FR-002**: `start_server.sh`는 서버 데몬 실행 전 하드웨어 가속 사전 점검(NVIDIA GPU, `nvidia-smi`, `nvcc` 및 llama_cpp CUDA 지원 여부)을 수행하고, 감지 실패 시 데몬 프로세스를 생성하지 않고 1 이상의 에러 코드로 종료해야 한다 (MUST).
- **FR-003**: `setup.sh`는 하드웨어 감지 결과를 프로젝트의 플랫폼 프로필 목록(`config/platform_profiles.json`)과 대조하여 현재 하드웨어와 가장 일치하는 프로필 이름을 사용자에게 출력하고 알맞은 CMAKE_ARGS를 전파해야 한다 (MUST).
- **FR-004**: `make_seed_pack.sh`는 아카이브 패키징 시 `config/platform_profiles.json` 설정을 반드시 포함해야 하며, 아카이브 생성 후 출력되는 이관 안내 메시지에 멀티 플랫폼 설정 및 `setup.sh` 감지 파이프라인에 대한 안내를 포함해야 한다 (MUST).
- **FR-005**: 고도화된 모든 쉘 스크립트는 기존의 서버 구동, 종료, 포트 바인딩 및 VRAM 해제 기본 동작과 100% 하위 호환성을 유지해야 한다 (MUST).

### Key Entities

- **운영 쉘 스크립트 세트**: `setup.sh`, `scripts/start_server.sh`, `scripts/stop_server.sh`, `scripts/status_server.sh`, `scripts/make_seed_pack.sh`로 구성된 서빙 제어 스크립트 모음
- **플랫폼 감지 리포트**: 쉘 스크립트 실행 시 운영자에게 표시되는 CPU, GPU, CMake 플래그, 프로필 매칭 요약 텍스트

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `./status_server.sh` 실행 시 5초 이내에 전체 멀티 플랫폼 하드웨어 리포트가 출력된다.
- **SC-002**: 하드웨어 가속 미지원 환경에서 `./start_server.sh` 실행 시 3초 이내에 감지 및 거부(fail-fast)되어 비정상 백그라운드 프로세스가 남지 않는다.
- **SC-003**: `./scripts/make_seed_pack.sh`로 생성된 Seed Pack 아카이브 파일 내에 `platform_profiles.json`이 100% 유실 없이 포함된다.
- **SC-004**: 쉘 스크립트 고도화 후 기존 환경에서의 start/stop/status 100% 호환 동작이 검증된다.

## Assumptions

- 쉘 스크립트는 POSIX 호환 Bash 환경에서 구동된다.
- `uv run python` 명령을 통해 `src.core.cpu_detector` 및 `src.core.config_manager`의 감지 결과를 쉘 스크립트에 파싱하여 전달할 수 있다.
- 타겟 머신에는 기본 개발 도구 및 리눅스 표준 커맨드(`bash`, `curl`, `tar`, `gzip` 등)가 설치되어 있다.
