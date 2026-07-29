# Feature Specification: Codebase Structural Audit & Real-world Test Reliability Verification

**Feature Branch**: `012-audit-test-reliability`

**Created**: 2026-07-29

**Status**: Draft

**Input**: User description: "테스트 코드를 먼저 작성하고, 코드 구현하고, 테스트 통과하고 다 구현했다고 하지만, 계속 실행이 안되고 있어, 이거 테스트 코드들을 믿을수 있어? 뭔가 지금 구조적으로 큰 문제가 있는것 같은데, 점검 분석 작업을 해야 할것 같아"

## Clarifications

### Session 2026-07-29

- Q: 외부 프로세스가 포트 8081을 점유하고 있을 때 시스템의 복구 및 예외 처리 정책을 어떻게 설정할까요? → A: 자율 복구(SIGTERM/SIGKILL)를 최우선 시도하고, 정리 불가능한 외부 프로세스일 경우 점유 PID 정보와 함께 PortCollisionError 예외를 발생시킨다.
- Q: CUDA 백엔드 실행부터 벤치마크 수행까지의 명확한 순차적 파이프라인 흐름은 어떻게 정의하는가? → A: 1) CUDA 지원 llama.cpp 런타임 탐색/선택, 2) 모델 로드 및 미존재 시 자동 다운로드, 3) 서빙 프로세스 개설(포트 정리 및 VRAM 100% 오프로드), 4) 비교 분석 벤치마크 실행의 4단계 선형 순서를 보장한다.
- Q: Antigravity Gemini 3.6 Flash 모델을 통해 합성/생성할 골든 데이터셋의 규모 및 보존 형태를 어떻게 설정할까요? → A: 전문 영역별(주식, 반도체, 금융, IT) 총 10개 대표 프롬프트-정답-루브릭 세트를 JSON 파일(data/golden_dataset.json)로 생성하여 영구 보존 및 벤치마크 평가 정답지로 활용한다.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 구조적 정밀 점검 및 실측 테스트 신뢰성 진단 (Priority: P1)

시스템 개발자는 단위/통합 테스트 수트(`pytest`)가 통과했음에도 실제 런타임 스크립트(`scripts/benchmark_quality.py --real`) 구동 시 발생하는 포트 충돌(`PortCollisionError`) 및 비동기 이벤트 루프 관련 오류의 구조적 원인을 명확히 진단받고, 테스트 코드와 실측 환경의 불일치를 근본적으로 해소하고자 한다.

**Why this priority**: 테스트 코드 성공 여부와 실제 시스템 동작 여부가 일치하지 않는 현상은 TDD 및 지속적 통합 환경의 신뢰성을 근본적으로 훼손하므로 가장 최우선적으로 해결되어야 한다.

**Independent Test**: `uv run pytest` 수행 결과와 `uv run python scripts/benchmark_quality.py --auto-download --real` 실제 실행 결과가 100% 동일한 성공 상태를 보장하는지 정밀 검증한다.

**Acceptance Scenarios**:

1. **Given** 포트 8081에 기존 프로세스가 존재하거나 재시작되는 상황, **When** `benchmark_quality.py --real` 또는 `spawn_process()`가 호출될 때, **Then** 예외 중단 없이 기존 프로세스를 안전하게 종료하고 포트를 클리어한 후 신규 모델 프로세스를 정상 개설한다.
2. **Given** Python 3.12 비동기 실행 환경, **When** 비동기 함수와 동기 스크립트 간 상호작용이 일어날 때, **Then** `DeprecationWarning: There is no current event loop` 또는 `RuntimeError: Event loop is closed` 예외가 일치하지 않도록 완벽히 제어된다.

---

### User Story 2 - 테스트 수트 Mock 환경과 실측 런타임 수렴성 강화 (Priority: P2)

개발팀은 단위 테스트에서 사용되는 과도한 모킹(Mocking)이 실제 소켓 결합, 외부 프로세스 제어, CUDA VRAM 할당 스펙을 은폐하지 않도록 테스트 수트를 재정비하고 실제 동작을 충실히 모사하는 통합 테스트를 확보하고자 한다.

**Why this priority**: 모킹이 실제 시스템 제약 조건을 제대로 반영하지 못하면 테스트 통과가 거짓 성공(False Positive)을 유발하므로 정합성 확보가 필수적이다.

**Independent Test**: 모킹 환경을 적용한 단위 테스트와 실환경 소켓/프로세스 바인딩을 검증하는 통합 테스트의 동작 계약이 완전히 동일한지 확인한다.

**Acceptance Scenarios**:

1. **Given** 단위/통합 테스트 수트 구동 시, **When** `MOCK_LLAMA_SERVER` 또는 `PYTEST_CURRENT_TEST` 환경 변수가 적용될 때, **Then** 테스트 실행 후 남아있는 비동기 잔여 태스크나 프로세스 소켓 자원이 완전히 해제된다.
2. **Given** 실제 GGUF 모델 로딩 시, **When** 모델 파일 존재 여부, VRAM 오프로드 비율, 포트 가용성 검사가 수행될 때, **Then** 테스트 코드와 실제 스크립트 간 호출 순서(Stop Process → Check Port Free → Spawn)가 동일하게 적용된다.

---

### User Story 3 - 6개 모델 실측 GPU 벤치마크 무중단 연속 수행 (Priority: P3)

운영자는 `benchmark_quality.py` 실행 시 6개 카탈로그 모델(Gemma 4 3종, Qwen 3.5 3종)에 대한 자동 다운로드, 프로세스 교체, 추론, VRAM 해제 및 기본 모델 원상 복원 라이프사이클이 단 한 번의 중단도 없이 완주되기를 원한다.

**Why this priority**: 품질 및 성능 비교를 위한 연속 실측 벤치마크가 중단 없이 완성되어야 서비스 안정성을 입증할 수 있다.

**Independent Test**: `python scripts/benchmark_quality.py --auto-download --real` 단일 명령어를 통해 6개 모델 벤치마크 전체 루프가 순차 성공함을 검증한다.

**Acceptance Scenarios**:

1. **Given** 6개 모델에 대한 자동 벤치마크 루프 구동 시, **When** 각 모델 전환 단계에 도달하면, **Then** 이전 모델의 VRAM 및 포트 8081 소켓이 완전히 해제된 후 다음 모델이 로드된다.

---

### Edge Cases

- 포트 8081이 외부 관리자 권한 프로세스나 알 수 없는 프로세스에 의해 고정 점유된 경우 시스템이 어떻게 반응해야 하는가?
- 비동기 테스트가 비정상 종료되어 이벤트 루프가 닫힌 상태에서 잔여 작업이 소멸 처리될 때 발생하는 예외는 어떻게 처리되어야 하는가?

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: 테스트 수트(`pytest`)와 실제 런타임 스크립트(`scripts/benchmark_quality.py`) 간 실행 결과 불일치 요소(포트 충돌, 이벤트 루프 경고) 100% 원인 분석 및 해결 명세 수립
- **DoD-002**: `ProcessManager` 내 프로세스 종료(`stop_process`)와 포트 가용성 검사(`detect_zombie_collision`, `_wait_for_port_free`)의 호출 순서 및 안정성 보장 구조 확립
- **DoD-003**: `uv run python scripts/benchmark_quality.py --auto-download --real` 단일 명령 실행 시 6개 모델 전체 루프가 예외 및 경고 없이 순차 수행됨을 실측으로 증명

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 시스템은 `ProcessManager.spawn_process()` 실행 시, 기존 프로세스 정리를 위한 `stop_process()` 및 `_wait_for_port_free()`를 포트 충돌 검사(`detect_zombie_collision()`)보다 먼저 수행하여 자기 프로세스 교체 시 포트 8081 점유 에러가 발생하는 구조적 결함을 원천 차단해야 한다.
- **FR-002**: 시스템은 Python 3.12 비동기 이벤트 루프 관리 메커니즘을 전면 보정하여 `_run_async` 래퍼를 포함한 동기-비동기 경계에서 `DeprecationWarning` 및 `RuntimeError: Event loop is closed` 경고/오류가 일절 발생하지 않도록 제어해야 한다.
- **FR-003**: 테스트 수트(`pytest`)는 실제 런타임 환경과의 계약(API 응답, 프로세스 생명주기, 포트 해제 순서)을 엄격히 동기화하여 Mock 성공이 실제 런타임 실패로 이어지는 허위 성공(False Positive) 현상을 없애야 한다.
- **FR-004**: 시스템은 `llama-server` 프로세스 오프로드 바이너리 선택 시 CPU 전용 바이너리를 배제하고 CUDA 기반 Python 런타임 백엔드(`sys.executable -m llama_cpp.server --n_gpu_layers -1`)를 최우선 적용하도록 스펙을 고정해야 한다.
- **FR-005**: 벤치마크 스크립트(`scripts/benchmark_quality.py`)는 모델 전환 간 포트 8081 소켓 해제 및 VRAM 수거를 보장하기 위해 최대 5초 지수 백오프(0.2s $\rightarrow$ 0.5s $\rightarrow$ 1.0s) 재시도 루프 및 명시적 동기화 간격을 준수해야 한다.
- **FR-006**: 단위/통합 테스트 수트는 테스트 종료 후 백그라운드 태스크나 서브프로세스가 남아있지 않도록 모든 Fixture에 명시적 리소스 해제(Tear-down) 로직을 강제해야 한다.
- **FR-007**: 시스템은 모델 파일 미존재, VRAM 용량 초과, 포트 점유 등의 예외 상황 발생 시 예외 객체 및 에러 상태(`ProcessStatusEnum.ERROR`) 반환 계약을 모든 관리자 컴포넌트 간에 일관되게 유지해야 한다.
- **FR-008**: 시스템은 벤치마크 및 서빙 프로세스 제어 시 [1. CUDA 가속 런타임 검증/선택] $\rightarrow$ [2. 모델 파일 자동 다운로드] $\rightarrow$ [3. 프로세스 개설 및 VRAM 100% 오프로드] $\rightarrow$ [4. 추론/벤치마크 실행]의 엄격한 선형 순차(Strict Sequential Pipeline) 계약을 준수해야 한다.
- **FR-009**: Antigravity AI 에이전트가 준비/개발 단계에서 전문 영역(주식, 반도체, 금융, IT) 총 10개 대표 프롬프트-정답-루브릭 세트로 구성된 레퍼런스 골든 데이터셋(`data/golden_dataset.json`)을 직접 합성/생성하여 로컬에 영구 보존하고, 벤치마크 구동 시 별도 외부 API 호출 없이 로컬 정답지(Ground Truth)로 로드하여 적용해야 한다.

### Key Entities

- **ProcessLifecycleState**: 프로세스의 현재 상태(`UNLOADED`, `LOADING`, `READY`, `ERROR`, `DOWNLOADING`), PID, 포트, VRAM 오프로드 여부, 에러 메시지를 보장하는 엔티티.
- **TestReliabilityContract**: 테스트 수트의 모킹 조건과 실측 런타임 시스템 동작 간 정합성을 검증하는 구조적 가이드라인.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `uv run python scripts/benchmark_quality.py --auto-download --real` 구동 시 100% 무에러 성공 완주.
- **SC-002**: `uv run pytest` 수행 시 74개 전체 테스트 통과 및 실행 후 잔여 백그라운드 태스크 수 0개 달성.
- **SC-003**: 런타임 스크립트 실행 로그 내 `PortCollisionError`, `DeprecationWarning`, `RuntimeError` 발생 건수 0건.

## Assumptions

- 실측 GPU 장비는 NVIDIA GeForce GTX 1080 Ti (11GB VRAM) 환경을 기준으로 동작한다.
- CUDA 지원 `llama-cpp-python` 패키지가 가상환경(`vllm-serv`) 내 정상 설치되어 있다.
- 포트 8081은 `ProcessManager`가 전전용으로 사용하는 기본 추론 포트이다.
