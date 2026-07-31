# Feature Specification: Real GPU Benchmark Engine & Dual-Mode (Mock vs Real) Automated Test Framework

**Feature Branch**: `specs/014-real-gpu-benchmark-testing`

**Created**: 2026-07-29

**Status**: Approved

**Input**: User description: "대체 왜, 테스트 코드는 다 통과 하면서, 실제로는 안돌아가냐고, 여전히 gemma4 e2b e4b 모델은 로드 안됨. 서버가 시작되면 cuda 활성화된 llama.cpp를 로드한다. 없으면 만든다. 서비스 모델 목록의 로컬 llm 파일들을 확인한다. 없으면 받는다. 기본 모델을 로드한다. 벤치마크 코드가 실행되면 순서대로 모델들을 로드하고, 요청에 응답하며 벤치마크 항목들을 진행한다. 벤치마크 항목을 모두 수행하면, 다음 모델을 로드한다. 모든 모델에 대해서 벤치마크가 진행되면 보고서를 작성한다. 벤치마크 항목을 통과하지 못한 모델에 대해서도 보고서에 내용을 작성한다. 이걸 구현하고, 이걸 테스트 하는 코드를 잘 작성해야 하는데, 대체 왜 테스트 코드에 목업을 집어넣은거야? 목업은 옵션으로 해야지, 테스트 코드가 목업 모드와 실제 모드를 나눠서 테스트 하게 되어있어야지, 하드코딩하거나 목업으로 회피하니까, 작업이 완료 되었다고 하고, 테스트 코드 통과했다고 하지만, 지금 스펙 몇개째 재작업중이야???"

---

## Executive Summary & User Value

본 피처는 단위/통합 테스트에서 Mock 데이터만으로 무조건적인 성공 결과를 내어 실제 라이브 GPU 환경(GTX 1080 Ti)에서 `llama-server` 프로세스 개설 및 `gemma4-e2b`, `gemma4-e4b` 모델 로딩 실패가 은폐되는 고질적인 테스트 신뢰도 문제를 근본적으로 해결하는 것을 목표로 합니다.

1. **자동 CUDA 빌드 및 종속성 확보**: 서버 시작 시 CUDA 지원 binary(`llama-server`)의 존재를 검증하고 미존재 시 소스 빌드 또는 바이너리를자동 로드/구축합니다.
2. **원스톱 모델 준비 및 자동 서빙 상주**: 서빙 카탈로그 상의 6개 모델 파일 존재 여부를 확인하고, 로컬 미존재 시 HuggingFace Hub에서 자동 다운로드 후 기본 서비스 모델(`qwen3.5-4b`)을 상주 서비스 상태로 즉시 로드합니다.
3. **순차 벤치마크 & 실패 내역 누락 없는 리포팅**: 벤치마크 실행 시 6개 모델을 순차 로드해 추론 테스트를 수행하며, OOM 또는 타임아웃으로 실패한 모델도 원인 메시지와 함께 보고서에 100% 표출합니다.
4. **듀얼 모드(Mock Mode vs Real GPU Mode) 테스트 체계 구축**: 모든 테스트 코드는 목업 전용 하드코딩을 배제하고, `TEST_MODE=mock` (CI/빠른 단위 테스트)과 `TEST_MODE=real` (실제 GPU 인퍼런스 및 실측 타임아웃 검증)을 환경 변수나 커스텀 pytest 파라미터(`pytest --real`)로 명확히 분리하여 실제 환경 동작을 완벽히 검증합니다.

---

## Clarifications

### Session 2026-07-29

- Q: `llama-server` 바이너리 자동 준비 방식 → A: 로컬 `llama.cpp` 소스 컴파일/빌드 (`cmake -B build -DGGML_CUDA=ON && cmake --build build`) 후 `.bin/llama-server` 생성.

---


## User Scenarios & Testing *(mandatory)*

### User Story 1 - CUDA LLM 서버 자동 로드 및 실측 인퍼런스 벤치마크 (Priority: P1)

**User Story**: AI 인프라 엔지니어 및 개발자는 서버 실행 시 CUDA 기반 llama-server 바이너리와 모델 파일이 자동 설치 및 준비되어, 6개 전체 모델에 대해 실제 GPU 추론 벤치마크를 순차 수행하고 성공/실패 여부를 누락 없이 확인하고 싶다.

**Why this priority**: 실제 GPU 런타임에서 모델 로드 실패나 타임아웃을 사전 차단하고 벤치마크 리포트의 신뢰성을 확보하는 가장 핵심적인 파이프라인입니다.

**Independent Test**: `python scripts/benchmark_quality.py --auto-download --real` 명령을 실행하여 CUDA 바이너리 확인 -> 6개 모델 로드 -> 추론 -> 리포트 생성 전 과정이 정상 동작하고 실패 모델도 표에 100% 표출됨을 확인.

**Acceptance Scenarios**:

1. **Given** 서버가 구동될 때, **When** 시스템에 CUDA 기반 llama-server 바이너리가 없으면, **Then** 빌드 또는 자동 다운로드를 수행하고 CUDA 가속 호환성을 검증한다.
2. **Given** 서비스 모델 카탈로그가 지정되면, **When** 로컬 디렉터리에 GGUF 모델 파일이 없으면, **Then** HuggingFace Hub에서 자동 다운로드를 완료한 뒤 기본 상주 모델(`qwen3.5-4b`)을 VRAM에 100% 오프로드하여 서빙 상주 상태로 개설한다.
3. **Given** 벤치마크 코드가 구동될 때, **When** 6개 모델(`gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`, `qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b`)을 순차 로드할 때 일부 모델이 헬스체크 타임아웃이나 OOM으로 실패하더라도, **Then** 실패 원인 메시지를 포함하여 final report 마크다운 표에 해당 모델 행을 100% 출력한다.

---

### User Story 2 - 테스트 코드의 듀얼 모드(Mock Mode vs Real GPU Mode) 분리 (Priority: P1)

**User Story**: QA 엔지니어 및 테스트 작성자는 테스트 수행 시 Mock 모드만으로 실측 오류가 은폐되는 현상을 막기 위해, 커맨드라인 옵션(`pytest --real` 또는 `TEST_MODE=real`)을 통해 실제 GPU 구동을 테스트하는 통합 테스트와 빠른 CI용 Mock 단위 테스트를 명확히 구별하여 실행하고 싶다.

**Why this priority**: Mock 테스트 통과만 믿고 실제 라이브 구동이 실패하는 거짓 성공(False Positive) 현상을 제거하고 개발 과정에서 실체적인 검증을 제공합니다.

**Independent Test**: `uv run pytest tests/integration/ -v --real` 구동 시 실제 CUDA 인퍼런스 서버를 띄워 실측 헬스체크 및 추론을 검증하고, `--real` 미지정 시에는 빠른 Mock 테스트로 동작함을 확인.

**Acceptance Scenarios**:

1. **Given** 테스트 수트 구동 시, **When** `pytest` 기본 구동(Mock Mode)일 때, **Then** 격리된 Mock 객체로 빠른 로직 검증을 수행한다.
2. **Given** 테스트 수트 구동 시, **When** `pytest --real` 또는 `TEST_MODE=real` 커스텀 플래그가 지정될 때, **Then** Mocking을 완전 해제하고 실제로 llama-server subprocess를 띄워 CUDA VRAM 로딩, HTTP REST API 응답, real inference 출력을 검증한다.

---

### User Story 3 - Gemma 4 (E2B / E4B / 12B) 및 Qwen 3.5 프로세스 생명주기 안정화 (Priority: P2)

**User Story**: 서비스 운영자는 Gemma 4 및 Qwen 3.5 모델 로딩 시 프로세스 파이프 버퍼 차단(deadlock)이나 CLI 인자 미호환으로 인한 헬스체크 타임아웃 없이 안전하게 모델 전환이 이루어지길 원한다.

**Why this priority**: 프로세스 개설 및 VRAM 해제/복원 루틴이 멈추지 않고 연속 실행되어 안정적인 서빙 전환을 보증합니다.

**Independent Test**: Gemma 4 E2B/E4B와 Qwen 3.5 4B 간의 5회 연속 서빙 전환 테스트 시 타임아웃이나 소켓 포트 충돌 없이 전환 완료.

**Acceptance Scenarios**:

1. **Given** Gemma 4 E2B/E4B 모델 로드 요청 시, **When** llama-server 로그 출력이 발생하더라도, **Then** 비동기 로그 드레인(Stream Drain)을 통해 PIPE 버퍼 블로킹 없이 헬스체크 200 OK를 리턴받는다.

---

### Edge Cases

- CUDA 드라이버나 NVIDIA GPU가 없는 시스템에서 Real GPU Mode 테스트 구동 시: 명확한 `GpuAccelerationError`를 발생시키고 테스트를 건너뛰거나(Skip with reason) 명시적 에러 메시지를 출력함.
- Gemma 4 모델 GGUF 로딩 시 멀티모달 CLIP 프로젝터 미존재 경고 발생 시: Pure Text LLM Serving 모드로 처리하여 로딩 지연 및 타임아웃을 방지함.

---

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `scripts/benchmark_quality.py --auto-download --real` 구동 시 Gemma 4 E2B, E4B 포함 6개 모델 전체의 순차 로딩, 실제 추론 및 마크다운 리포트 완성이 정상 동작함.
- **DoD-002**: `pytest` 실행 옵션에 `--real` 커스텀 플래그 및 듀얼 모드 Fixture(`test_mode`)가 추가되어, Mock 모드와 Real GPU 모드가 각각 엄격하게 검증됨.
- **DoD-003**: 6개 모델 벤치마크 및 듀얼 모드 테스트 수트 전체(Mock & Real)가 100% 통과함.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (CUDA llama-server 바이너리 검증 및 빌드/로드)**: 서버 시작 시 시스템에서 CUDA 가속이 가능한 `llama-server` 바이너리 위치를 검증하고, 미존재 시 로컬 `llama.cpp` 소스를 CMake (`cmake -B build -DGGML_CUDA=ON && cmake --build build`)로 컴파일하여 `.bin/llama-server` 바이너리를 생성 후 GPU 인퍼런스 엔진으로 로드해야 한다.
- **FR-002 (모델 자동 다운로드 & 기본 상주 모델 로드)**: 서비스 모델 카탈로그 6개 모델의 GGUF 파일 경로를 확인하고, 미존재 시 HuggingFace Hub에서 원스톱 자동 다운로드를 수행한 후 기본 서비스 모델(`qwen3.5-4b`)을 상주 상태로 개설해야 한다.
- **FR-003 (실시간 순차 벤치마크 & 실패 내역 보존 리포팅)**: 벤치마크 구동 시 카탈로그 상 6개 모델을 순차적으로 로드해 추론을 수행하고, 실패하거나 헬스체크 타임아웃이 발생한 모델이라도 에러 메시지와 함께 마크다운 리포트 표에 100% 기록해야 한다.
- **FR-004 (듀얼 모드 테스트 체계: Mock vs Real)**: Pytest 실행 시 `--real` 커스텀 플래그를 지원하여, Mock 모드(`TEST_MODE=mock`)에서는 빠른 단위 검증을 수행하고, Real 모드(`TEST_MODE=real`)에서는 실제 GPU 프로세스를 개설하여 Real HTTP 추론 및 헬스체크를 검증하는 듀얼 모드 테스트 Fixture를 제공해야 한다.
- **FR-005 (하드코딩/회피 목업 전면 금지 및 Real Mode 검증)**: Real Mode 테스트 실행 시 하드코딩된 dummy response 반환이나 목업 객체 덮어쓰기를 엄격히 금지하고, 실제 `ProcessManager`와 HTTP API 통신 결과를 검증해야 한다.
- **FR-006 (Gemma 4 비동기 스트림 드레인 및 서빙 개설)**: `ProcessManager`는 프로세스 실행 시 발생되는 stdout/stderr 로그 스트림을 비동기로 계속 드레인하여 OS PIPE 버퍼 교착 상태를 방지하고 Gemma 4 및 Qwen 3.5 모델의 서빙 READY 상태를 보장해야 한다.

### Key Entities

- **TestExecutionMode**: `MOCK` 및 `REAL`을 구분하는 테스트 실행 모드 열거형.
- **RealGpuBenchmarkSession**: 6개 모델 파일 다운로드, llama-server 구동, 실측 추론, 리포트 작성을 관리하는 세션 객체.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001 (Real Mode GPU 추론 성공률)**: Real Mode (`pytest --real`) 구동 시 6개 모델의 실측 인퍼런스 헬스체크 및 추론 테스트 성공률 100%.
- **SC-002 (6개 모델 리포트 누락률)**: 벤치마크 실행 후 생성된 마크다운 보고서에 6개 모델 행이 0개 누락으로 100% 기재됨.
- **SC-003 (테스트 듀얼 모드 분리도)**: Mock 테스트와 Real GPU 테스트가 커스텀 플래그(`--real`)로 100% 명확히 구분 및 제어됨.

---

## Assumptions

- **GPU 하드웨어**: NVIDIA GeForce GTX 1080 Ti (11GB VRAM) 환경에서 CUDA 드라이버 및 PyNVML이 지원됨.
- **Python / Pytest**: Pytest 실행 시 `conftest.py`에 `--real` 커스텀 option fixture가 추가되어 실행 환경을 직접 인스펙션할 수 있음.
