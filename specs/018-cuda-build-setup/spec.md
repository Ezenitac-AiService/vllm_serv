# Feature Specification: Automated CUDA-Enabled llama.cpp Build & Setup Pipeline

**Feature Branch**: `specs/018-cuda-build-setup`

**Created**: 2026-07-29

**Status**: Draft

**Input**: User description: "setup.sh로 셋팅했더니 llama.cpp가 cuda 지원 플래그 없이 빌드된거 같아"

---

## Executive Summary & User Value

본 피처는 `setup.sh` 파이프라인 및 `ProcessManager` 구동 시 NVIDIA GPU 환경에서 `llama.cpp` 및 `llama-cpp-python` 서빙 모듈이 CUDA 가속 지원 플래그(`GGML_CUDA=ON`)로 자동 검증·빌드·설치되도록 보장하는 시스템 개선 사양입니다.

개발자 및 시스템 운영자는 `./setup.sh` 수동 및 자동 환경 구성 후 서빙 프로세스를 구동할 때 `llama_supports_gpu()` 및 NVIDIA `nvtop` / `nvidia-smi`를 통해 GPU VRAM에 가중치가 100% 탑재(Offload)되는 실제 GPU 인퍼런스를 보장받습니다.

---

## Clarifications

### Session 2026-07-29

- Q: CUDA 빌드 실패 시 setup.sh 동작 정책은? → A: Option A (CUDA/nvcc 미존재 또는 소스 컴파일 실패 시 CPU 전용 폴백 없이 명확한 오류 메시지와 함께 setup.sh 즉시 중단).

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - setup.sh 실행 시 CUDA 기반 llama-cpp-python 자동 빌드 및 의존성 동기화 (Priority: P1)

**User Story**: 개발자는 `./setup.sh` 실행 시 CPU 전용 휠 대신 NVIDIA CUDA 가속 옵션(`GGML_CUDA=ON`)이 포함된 `llama-cpp-python` 서빙 패키지가 가상환경에 자동 동기화 설치되어 `nvtop`에 인퍼런스 프로세스가 잡히길 원한다.

**Why this priority**: CPU 전용 서빙 롤백을 차단하고 GTX 1080 Ti 등 NVIDIA GPU 가속 성능을 100% 발휘하기 위한 최우선 기반 요구사항입니다.

**Independent Test**: `./setup.sh` 완료 후 `uv run python -c "import llama_cpp; assert llama_cpp.llama_supports_gpu()"` 검증 성공.

**Acceptance Scenarios**:

1. **Given** NVIDIA GPU 및 `nvcc` / CUDA 개발 환경이 존재하는 서버에서, **When** `./setup.sh`가 실행될 때, **Then** `pyproject.toml` 및 `uv` 설치 파이프라인에 CUDA 가속 빌드 환경변수(`CMAKE_ARGS="-DGGML_CUDA=on"`)를 적용하여 `llama_supports_gpu()`가 `True`를 반환하도록 고정한다.
2. **Given** `./setup.sh` 내 `uv sync`가 실행될 때, **When** 가상환경 동기화가 이루어지면, **Then** CUDA 지원 `llama-cpp-python[server]` 패키지가 언인스톨되지 않고 보존된다.

---

### User Story 2 - ProcessManager C++ llama-server CMake CUDA 자동 컴파일 보완 (Priority: P2)

**User Story**: 개발자는 독립 바이너리 빌드가 필요할 때 `ProcessManager`가 `llama.cpp` C++ 소스로부터 `cmake -B build -DGGML_CUDA=ON` 명령을 실행하여 고성능 네이티브 `llama-server` 바이너리를 자동 빌드 및 배치하길 원한다.

**Why this priority**: Python 모듈 overhead 없는 네이티브 C++ Cuda 서버 바이너리를 확보하여 최적의 추론 속도 및 메모리 효율을 달성하기 위함입니다.

**Independent Test**: `ProcessManager.verify_and_build_llama_server()` 실행 시 `.bin/llama-server` CUDA 바이너리가 자동 생성되고 실행 가능함을 확인.

**Acceptance Scenarios**:

1. **Given** `llama-server` 바이너리가 `.bin/`에 미존재할 때, **When** `verify_and_build_llama_server()`가 구동되면, **Then** `GGML_CUDA=ON` 플래그를 주입하여 CMake 빌드를 수행하고 `.bin/llama-server`로 자동 복사한다.

---

### User Story 3 - nvtop & nvidia-smi GPU VRAM 모니터링 무결성 검증 (Priority: P2)

**User Story**: 운영자는 `nvtop` 및 `nvidia-smi` 터미널 모니터링 도구에서 서빙 프로세스(PID) 및 모델 VRAM 점유량(예: 2GB~9GB)이 정확히 실시간 시각화되길 원한다.

**Why this priority**: 실제로 GPU VRAM이 할당되어 가속되고 있음을 투명하게 모니터링하기 위함입니다.

**Independent Test**: `./status_server.sh` 및 `nvidia-smi` 조회 시 `llama-server` / `python` PID가 GPU 프로세스 목록 및 VRAM 메모리 사용량에 정상 등록됨을 확인.

**Acceptance Scenarios**:

1. **Given** 기본 모델 `qwen3.5-4b` 서빙이 READY 상태일 때, **When** `nvidia-smi` 또는 `nvtop`을 실행할 때, **Then** 유휴 VRAM(133MB)이 아닌 모델 탑재 VRAM 메모리(2,500MB 이상) 및 프로세스 PID가 명확히 감지된다.

---

### Edge Cases

- 서버에 NVIDIA CUDA 라이브러리(`nvcc`)가 누락되거나 빌드 실패 시: CPU 전용 롤백을 수행하지 않고 `setup.sh`를 즉시 중단하며 CUDA 구성을 안내한다.
- `uv sync` 수행 시 외부 PyPI에서 CPU 전용 휠을 강제 덮어쓰는 경우: `pyproject.toml` 설정 및 빌드 환경 제어로 CUDA 빌드가 유지되도록 방어한다.

---

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `./setup.sh` 파이프라인 재실행 후 `llama_supports_gpu()`가 `True`를 반환함을 검증.
- **DoD-002**: `pyproject.toml`에 `llama-cpp-python[server]` 명시 및 `uv sync` 후 패키지 유지 확인.
- **DoD-003**: `nvidia-smi` 및 `nvtop` 모니터링에서 모델 탑재 VRAM 메모리 및 PID가 정상 감지됨을 확인.
- **DoD-004**: 전체 `pytest` 수트 (`uv run pytest -v`) 100% 통과 보장.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (setup.sh CUDA 빌드 파이프라인 강형화)**: `./setup.sh` 실행 시 `CMAKE_ARGS="-DGGML_CUDA=on"` 및 CUDA 휠 빌드를 지정하여 `llama-cpp-python`이 CUDA 지원 상태로 가상환경에 설치되도록 보장해야 한다.
- **FR-002 (pyproject.toml 의존성 영구 등록)**: `pyproject.toml` 의존성 항목에 `llama-cpp-python[server]`를 명시하여 `uv sync` 실행 시 CUDA 패키지가 삭제되지 않도록 보장해야 한다.
- **FR-003 (ProcessManager CMake CUDA 플래그 명시)**: `ProcessManager.verify_and_build_llama_server()`에서 CMake 빌드 수행 시 `-DGGML_CUDA=ON` 옵션을 확실히 전달하여 C++ 바이너리를 빌드해야 한다.
- **FR-004 (GPU VRAM 점유 및 nvtop 감지 검증)**: 모델 서빙 개설 후 단순 헬스체크 200 응답뿐만 아니라 실시간 `nvidia-smi` 프로세스 점유 및 VRAM 메모리 할당을 검증해야 한다.
- **FR-005 (CUDA 환경 부재 시 즉시 중단 방어)**: NVIDIA GPU 또는 `nvcc` CUDA 툴킷 미존재 시 `setup.sh`는 CPU 전용 폴백을 거부하고 명확한 예외 메시지와 함께 즉시 중단되어야 한다.

### Key Entities

- **CudaBuildPipeline**: `setup.sh` 및 `ProcessManager`에서 CUDA가속 플래그(`GGML_CUDA=on`)를 주입하여 바이너리 및 모듈을 엮어내는 빌드 구성체.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001 (GPU 지원 검증)**: `llama_cpp.llama_supports_gpu()` 호출 결과 `True` 달성.
- **SC-002 (VRAM 점유율)**: `qwen3.5-4b` 서빙 시 GPU VRAM 실측 할당량 2,000MB 이상 및 PID 감지.
- **SC-003 (테스트 통과율)**: `uv run pytest -v` 전체 수트 100% 통과.

---

## Assumptions

- 시스템 환경에 NVIDIA GPU 드라이버 및 `/usr/bin/nvcc` CUDA 툴킷이 설치되어 있음.
- `cmake` 및 `ninja` 빌드 툴이 가상환경 또는 시스템 PATH에 준비되어 있음.
