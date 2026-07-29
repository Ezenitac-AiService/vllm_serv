# Feature Specification: 코드베이스 구조 개선 및 효율화 리팩토링 (Codebase Efficiency Refactoring)

**Feature Branch**: `006-codebase-efficiency-refactoring`

**Created**: 2026-07-29

**Status**: Draft

**Input**: User description: "기능과 요구사항을 유지하거나 개선하면서, 효율성을 올리고 코드 구조를 개선하는 리펙토링"

## Clarifications
### Session 2026-07-29 (Critical Review Enhancements)
- Q: Atomic Replace 시 교차 디바이스(EXDEV) 마운트 에러 방지 방법 → A: `tempfile.NamedTemporaryFile` 생성 시 반드시 대상 설정 파일과 동일한 디렉토리 (`dir=os.path.dirname(config_path)`) 내에 임시 파일을 생성 후 `os.replace` 수행.
- Q: `httpx.AsyncClient` 소켓 누수 방지 및 수명주기 관리 → A: FastAPI `lifespan` 내에서 커넥션 풀을 초기화하고 종료 시 `aclose()`를 명시적으로 호출하여 자원 해제.
- Q: 클라이언트 이탈 시 역방향 프록시 스트림 자원 낭비 방지 → A: `request.is_disconnected()` 체크를 통한 즉시 스트림 캔슬레이션 및 모델별 동적 `Retry-After` 산출 적용.

### Session 2026-07-29 (Multi-Persona Deep Analysis Enhancements)
- Q: [Architect Persona] 비동기 이벤트 디스패칭 메모리 백프레셔 방지 → A: `EventBroadcaster`의 비동기 큐에 Bounded Queue(`maxsize=100`) 적용 및 오버플로우 방지 전략 수립.
- Q: [SRE Persona] `httpx.AsyncClient` 커넥션 풀 한계 설정 → A: `httpx.Limits(max_keepalive_connections=20, max_connections=100)` 기반 커넥션 한계 명시.
- Q: [Security Persona] SSE 실시간 연결 좀비화 차단 → A: 15초 주기 주석 패킷(`: ping\n\n`) 하트비트를 SSE 이벤트 스트림에 주입하여 방화벽 타임아웃 및 좀비 소켓 차단.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 서브프로세스 관리 및 이벤트 디스패치 구조 분리 (Priority: P1)

관리자 및 백엔드 개발자는 LlamaManager가 단일 클래스 내에 프로세스 실행, 링커 구독 제어, VRAM 한계 조회 등 과도한 책임을 가졌던 기존 구조를 모듈화된 하위 컴포넌트로 분리하여, 모델 로딩/언로드 및 실시간 이벤트 전송이 더욱 빠르고 안정적으로 동작하기를 원합니다.

**Why this priority**: LlamaManager가 핵심 서빙 백엔드 엔진이므로 책임 분리(SRP) 및 비동기 상태 관리 개선이 전체 안정성과 성능에 가장 높은 영향을 미칩니다.

**Independent Test**: 하위 서브프로세스 실행 모듈 및 이벤트 디스패처 모듈을 독립적인 단위 테스트로 검증하며, 기존 모델 로드/언로드 및 SSE 상태 스트림 API 동작이 동일하게 유지되는지 통합 테스트로 확인합니다.

**Acceptance Scenarios**:

1. **Given** 모델 교체 요청이 들어왔을 때, **When** LlamaManager가 신규 모델 로딩 프로세스를 스폰하면, **Then** 이벤트 디스패처가 독립 비동기 큐를 통해 프론트엔드 구독자들에게 지연 없이 상태 변화를 즉시 방송한다.
2. **Given** 하위 프로세스가 예기치 못하게 종료되거나 에러가 발생했을 때, **When** 프로세스 모니터가 이를 감지하면, **Then** 메인 서빙 루프 블로킹 없이 에러 상태 및 메시지를 안전하게 갱신하고 SSE로 전파한다.

---

### User Story 2 - 원자적 파일 I/O 및 설정 관리 모듈 안정성 강화 (Priority: P1)

시스템은 ConfigManager의 파일 읽기/쓰기 동작을 원자적(Atomic) I/O 방식으로 개선하고 메모리 캐싱 전략을 적용하여, 동시 다발적인 설정 갱신 시 파일 손상 위험을 방지하고 I/O 병목을 최소화해야 합니다.

**Why this priority**: 동시 접속자 또는 빠른 연속 설정 변경 요청 시 발생할 수 있는 JSON 파일 락/손상 예외를 방지하여 설정 영속성 보장성을 높입니다.

**Independent Test**: 동일 디렉토리 내 임시 파일 작성 후 원자적 교체(atomic replace) 방식을 시뮬레이션하는 단위 테스트를 작성하여, 동시 갱신 상황에서도 데이터 정합성이 유지되는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** 여러 라우터 요청에서 동시에 설정 변경을 시도할 때, **When** ConfigManager가 설정을 업데이트하면, **Then** 동일 디렉토리 내 임시 파일 쓰기 후 atomic rename(`os.replace`)을 사용하여 EXDEV 에러 없이 설정 파일이 손상되지 않고 정상 반영된다.
2. **Given** 서버 구동 중 설정 조회가 자주 발생할 때, **When** `get_config()`를 호출하면, **Then** 불필요한 디스크 I/O를 최소화하고 메모리 캐시를 유효하게 활용하여 신속하게 설정값을 반환한다.

---

### User Story 3 - 라우터/미들웨어 비동기 프록시 효율화 및 코드 가독성 개선 (Priority: P2)

개발자는 API 라우터 계층(`inference_api.py`, `dashboard_api.py`)에 타입 힌트, Pydantic 데이터 모델, 명확한 예외 처리 및 비동기 HTTP 클라이언트 커넥션 풀링을 적용하여 코드 가독성과 네트워크 릴레이 효율성을 극대화하고 싶어 합니다.

**Why this priority**: 프록시 계층의 오버헤드를 낮추어 추론 요청 중계 지연 시간을 줄이고 유지보수성을 향상시킵니다.

**Independent Test**: 프록시 API 호출 시 기존 503 Maintenance Mode 및 정상 추론 응답 전달이 동일하게 작동하는지 통합 테스트 스위트로 검증합니다.

**Acceptance Scenarios**:

1. **Given** 추론 API(`/v1/chat/completions`) 요청이 들어왔을 때, **When** 하위 `llama-server`로 스트리밍 프록시를 수행하면, **Then** FastAPI lifespan 기반 커넥션 풀(HTTP Connection Pool)을 재활용하여 신속하고 안정적으로 스트리밍 응답을 중계하고 이탈 시 캔슬한다.
2. **Given** 전체 테스트 스위트(`pytest`)를 구동할 때, **When** 리팩토링된 코드를 대상으로 실행하면, **Then** 100% 테스트 통과 및 실행 속도 향상을 달성한다.

---

### Edge Cases

- 설정 파일 쓰기 중 OS 전원 차단이나 디스크 용량 부족 시 동일 디렉토리 원자적 쓰기가 이전 유효 설정 파일을 안전하게 보존하는가?
- 하위 서브프로세스 킬 시 타임아웃 발생 상황에서 비동기 타임아웃 이벤트가 정확히 캐치되어 강제 종료(`SIGKILL`)로 안전하게 에스컬레이션되는가?
- 외부 클라이언트가 프록시 요청 도중 접속을 조기 차단했을 때 하위 프록시 커넥션이 즉시 정리되는가?

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: 기존 외부 API 규격(FastAPI 라우트, SSE 데이터 포맷, 503 헤더 등) 및 모든 기존 테스트 스위트(10개)가 100% 통과하고 하위 호환성을 유지해야 한다.
- **DoD-002**: LlamaManager 및 ConfigManager의 책임 분리(SRP) 및 동일 디렉토리 원자적 파일 쓰기 모듈에 대한 전용 단위 테스트가 작성되고 통과해야 한다.
- **DoD-003**: 코드 가독성 및 타입 힌팅이 개선되고, 모든 모듈에서 비동기 처리 및 커넥션 풀 자원 누수 병목이 제거되어야 한다.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 시스템은 기존 기능 및 요구사항(모델 동적 교체, 503 Maintenance Mode, SSE 실시간 동기화, 단일 토큰 인증 등)을 100% 변경 없이 그대로 유지해야 한다.
- **FR-002**: LlamaManager는 서브프로세스 라이프사이클 관리자(`ProcessManager`)와 SSE 구독/이벤트 전파자(`EventBroadcaster`)로 모듈화 분리되어야 하며, 이벤트 큐는 메모리 누수 방지를 위한 Bounded Queue(`maxsize=100`)를 적용해야 한다.
- **FR-003**: ConfigManager는 동시 쓰기 시 교차 디바이스(EXDEV) 에러 방지 및 데이터 오염 방지를 위해 대상 설정 파일과 동일한 디렉토리(`dir=os.path.dirname(config_path)`) 내 임시 파일 생성 후 Atomic Replace 방식으로 파일 영속화를 수행해야 한다.
- **FR-004**: HTTP 역방향 프록시(`inference_api.py`)는 FastAPI `lifespan` 내에서 바인딩되는 싱글톤 `httpx.AsyncClient` 커넥션 풀(`httpx.Limits(max_connections=100)`)을 효율적으로 재사용하고 종료 시 명시적 `aclose()`를 호출하여 소켓 낭비와 연결 지연을 최소화해야 한다.
- **FR-005**: 모든 핵심 모듈에 명확한 Python 타입 힌트(Type Annotations)와 Pydantic/DataClass 기반 데이터 구조를 적용하여 코드 가독성과 유지보수성을 극대화해야 한다.
- **FR-006**: 추론 역방향 프록시 스트리밍 시 클라이언트 접속 이탈(`request.is_disconnected()`)을 감지하여 하위 업스트림 스트림 요청을 중단하고 자원을 즉시 해제해야 한다.
- **FR-007**: SSE 이벤트 스트림 브로드캐스터는 15초 주기 주석 패킷(`: ping\n\n`) 하트비트를 주입하여 방화벽 커넥션 드롭 및 좀비 연결을 방지해야 한다.
- **FR-008**: ConfigManager의 임시 파일 생성 시 소유자 전용 권한(`os.chmod(tmp_path, 0o600)`)을 명시하여 로간 토큰 유출을 원천 방지해야 한다.
- **FR-009**: ProcessManager는 `SIGKILL` 전송 후 `await process.wait()`를 호출하여 OS 커널좀비 프로세스(`<defunct>`) 수거를 보장해야 한다.
- **FR-010**: 역방향 프록시 스트림 제너레이터는 `try...finally` 내에서 `await response.aclose()`를 실행하여 예외 발생 시 `httpx` 커넥션 풀 오염을 방지해야 한다.
- **FR-011**: EventBroadcaster는 Bounded Queue 오버플로우 발생 시 최신 전체 상태 스냅샷(`Full Status Snapshot`)을 주입하여 대시보드 UI 고립을 방지해야 한다.

### Key Entities

- **ProcessState**: 프로세스 상태(LOADING, READY, UNLOADED, ERROR) 및 에러 메시지, 리턴 코드를 캡슐화한 불변 상태 객체 (Pydantic v2 `frozen=True`)
- **EventPayload**: SSE로 브로드캐스트되는 서버 현황 데이터 포맷 (상태, 현재 모델, n_ctx, VRAM 사용량 등)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 기존 10개 단위/통합 테스트 스위트 성공률 100% 유지.
- **SC-002**: 동일 디렉토리 원자적 파일 I/O 도입으로 동시 설정 변경 시 JSON 파일 손상 및 EXDEV 마운트 에러 가능성 0% 달성.
- **SC-003**: 모듈 책임 분리를 통해 `llama_manager.py` 단일 파일 라인 수를 줄이고 코드 결합도(Coupling)를 대폭 감소시킵니다.

## Assumptions

- 기존 소스 코드 파일 경로(`src/core/`, `src/api/`) 구조 내에서 내부 모듈 리팩토링이 진행되며, 외부 패키지 API 엔드포인트URL은 전혀 변경되지 않는다고 가정한다.
- 임시 파일 생성을 위한 파일 시스템 오퍼레이션(`os.replace` 또는 `tempfile`)이 해당 환경에서 원자적(Atomic) 연산을 지원한다고 가정한다.
