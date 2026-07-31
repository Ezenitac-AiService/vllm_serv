# Feature Specification: Codebase Refactoring, Modularity & Architecture Optimization

**Feature Branch**: `specs/017-codebase-refactoring-cleanup`

**Created**: 2026-07-29

**Status**: Approved

**Input**: User request: "리펙토링: 하드코딩 된 내용이 없는가? 비효율적인 구조로 되어있는 부분은 없는가? 계층적 모듈화는 잘 되어있는가? 너무 어렵고, 복잡한 추상화가 되어있는 부분은 없는가? 구조와 로직을 파악하기 쉬운 모듈화가 되어있는가? (사설 내부망 192.168.0.x 대역 RAG 및 Agent 서비스 전용 LLM 서빙 포함)"

---

## Executive Summary & User Value

본 피처는 `vllm_serv` 전체 파이썬 소스 코드 및 관련 인프라에 대한 **종합 리팩토링 및 아키텍처 고도화 작업**을 규정합니다.

사용자의 정밀 감사 및 RAG/Agent 서빙 요구사항에 따라 아래 5대 핵심 영역을 체계적으로 검증 및 개정합니다:
1. **하드코딩 완전 제거 (Zero Hardcoding)**: 포트, 호스트 URL, 파일 경로, VRAM 용량 한계, 타임아웃 등 모든 매개변수의 외부 설정 JSON (`config/model_catalog.json`, `config/server_config.json`) 및 환경변수 모듈화 검증.
2. **비효율적 구조 및 불필요한 중복 제거**: 중복 카탈로그 딕셔너리 정의, 불필요한 객체 재생성, 중복 헬스체크 폴링 구문 정리.
3. **명확한 계층적 모듈화 (Hierarchical Modularity)**: API 라우팅 레이어(`src/api`), 비즈니스 코어 레이어(`src/core`), 평가 엔지니어링 레이어(`src/eval`), 실행 스크립트 레이어(`scripts/`) 간 단방향 의존성 및 결합도(Coupling) 최소화.
4. **실용적이고 직관적인 추상화 (Pragmatic Abstraction)**: 과도하게 복잡하거나 불필요한 N중 인터페이스 감싸기(Wrapper)를 배제하고, 신규 개발자가 파악하기 쉬운 가독성 높은 구조 정립.
5. **RAG & Agent 마이크로서비스 전용 사설망(192.168.0.x) 고성능 서빙**: `192.168.0.x` 대역에서 실행되는 RAG (문서 검색 컨텍스트) 및 AI Agent (멀티턴/도구 호출) 서비스의 고동시성 API 요청을 비동기 스트리밍(SSE)과 IP CIDR 접근 제어로 안전하고 병목 없이 처리.

---

## Clarifications

### Session 2026-07-29

- Q: 프로세스 관리 무결성 및 외부 네트워크 무단 노출 보안 방어 방식은? → A: `0.0.0.0` 무제한 인터넷 개방을 금지하고, 포트포워딩이 불가능한 내부망 사설 대역(`192.168.0.0/24`) 및 `127.0.0.1`에서만 접근 가능하도록 `config/server_config.json` CIDR 허용 IP 필터 미들웨어 및 바인딩 적용.
- Q: RAG 및 Agent 마이크로서비스 연동 서빙 요구사항은? → A: `192.168.0.x` IP 대역의 RAG 서비스(긴 문서 컨텍스트 검색) 및 Agent 서비스(멀티턴/도구 호출 스트리밍)가 전송하는 `POST /v1/chat/completions` 요청을 병목 없이 처리하는 고성능 비동기 LLM 백엔드로 정립.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 하드코딩 전면 제거 및 설정 외부화 검증 (Priority: P1)

**User Story**: 인프라 운영자 및 개발자는 코드 수정 없이 외부 설정 파일(`config/model_catalog.json`, `config/server_config.json`)과 환경변수 설정만으로 포트, 호스트, VRAM 한계, 모델 카탈로그를 완벽히 동적 제어하길 원한다.

**Why this priority**: 다양한 배포 환경에서 소스 코드 변경 없는 유연성을 확보하고, 하드코딩으로 인한 잠재적 오류를 사전에 차단하기 위함입니다.

**Independent Test**: `uv run pytest tests/unit/test_config_manager.py -v` 실행 시 모든 하드코딩 상수가 외부 설정으로부터 정상 동적 로드됨을 확인.

**Acceptance Scenarios**:

1. **Given** `config/server_config.json` 또는 환경변수 `LLAMA_PORT` / `LLAMA_HOST`가 변경될 때, **When** 서버 및 프로세스 매니저가 개설될 때, **Then** 파이썬 코드 내의 하드코딩 포트(`8081` 등)를 참조하지 않고 지정된 가변 설정값을 100% 적용한다.
2. **Given** 모델 카탈로그 정보 조회가 필요할 때, **When** `ProcessManager`, `ModelDownloader`, `inference_api.py`가 동시 참조할 때, **Then** 중복 딕셔너리 정의 없이 `ConfigManager.get_model_catalog()` 단일 진실 소스(Single Source of Truth)에서 로드한다.

---

### User Story 2 - 계층적 모듈화 및 직관적 추상화 정립 (Priority: P1)

**User Story**: 신규 참여 개발자 및 유지보수 담당자는 API 라우팅, 프로세스 제어, 모델 다운로드, 평가 엔진이 과도한 추상화 레이어 없이 직관적으로 계층 분리되어 로직을 한눈에 파악하길 원한다.

**Why this priority**: 가독성 향상 및 디버깅 용이성을 높여 개발 생산성과 코드 무결성을 증진시키기 위함입니다.

**Independent Test**: `src/api`, `src/core`, `src/eval` 각 모듈을 독립적으로 단원 테스트하여 순환 참조(Circular Import) 및 상호 직접 강결합 오류 0건 검증.

**Acceptance Scenarios**:

1. **Given** REST API 요청 수신 시, **When** FastAPI 라우터가 작동할 때, **Then** 라우터는 라우팅 및 HTTP 규격 처리에만 집중하고 실제 서빙 생명주기는 `src/core` 코어 모듈로 깔끔히 위임한다.
2. **Given** 불필요하게 깊은 N중 상속이나 과도한 래퍼 함수가 존재하는 경우, **When** 리팩토링을 수행할 때, **Then** 직관적인 단일 책임을 가진 파이썬 클래스/함수로 단순화한다.

---

### User Story 3 - 사설 내부망(192.168.0.x) 전용 보안 접근 제어 (Priority: P2)

**User Story**: 보안 담당자 및 네트워크 관리자는 외부 인터넷망에서의 무단 접근은 차단되고, 포트포워딩 되지 않는 사설 내부망(`192.168.0.x`) 기기에서만 안전하게 LLM API에 접속할 수 있길 원한다.

**Why this priority**: 인터넷 무단 노출 공격 표면(Attack Surface)을 사전에 완전히 차단하면서 내부망 팀원 간의 인퍼런스 서빙 협업을 보장하기 위함입니다.

**Independent Test**: `192.168.0.x` 대역 IP에서 `curl http://192.168.0.X:8081/health` 호출 시 200 OK 허용 및 허용되지 않은 타 공인 IP 접속 시 403 Forbidden 차단 검증.

**Acceptance Scenarios**:

1. **Given** 서버 구동 시 `config/server_config.json`에 `allowed_subnets: ["127.0.0.1", "192.168.0.0/24"]`가 설정될 때, **When** 클라이언트 요청이 도달할 때, **Then** `192.168.0.x` 사설 대역 접근은 100% 정상 허용하고 그 외 무단 IP 접근은 403 차단한다.

---

### User Story 4 - RAG 및 Agent 마이크로서비스 연동 고성능 서빙 (Priority: P2)

**User Story**: `192.168.0.x` 사설 IP 대역에서 동작하는 RAG 파이프라인 및 AI Agent 서비스는 `vllm_serv`를 백엔드 LLM 엔진으로 사용하여 긴 문서 컨텍스트 조율 및 실시간 토큰 스트리밍 생성을 안정적으로 처리받길 원한다.

**Why this priority**: RAG 서비스의 긴 문서 청크 처리와 AI Agent의 실시간 대화 응답 성능을 보장하기 위함입니다.

**Independent Test**: RAG 검색 컨텍스트 대용량 토큰(`n_ctx=8192` 이상) 및 Agent 스트리밍(`stream=true`) 요청 동시 수용 검증.

**Acceptance Scenarios**:

1. **Given** RAG 또는 Agent 서비스가 `POST /v1/chat/completions` 요청을 전송할 때, **When** 스트리밍 옵션(`stream=true`)이 포함되면, **Then** SSE (Server-Sent Events) 표준 델타 토큰을 무분할 동시 스트리밍 반환한다.

---

## Edge Cases

- 설정 파일 (`config/server_config.json`) 파싱 에러 시: 인라인 기본 안전 내장값(Fallback Default)을 읽어오고 경고 로그 출력.
- 환경변수와 JSON 파일 간 설정 충돌 시: 환경변수 설정이 최우선 적용되도록 명확한 덮어쓰기 순서 보장.
- 미사용 레거시 함수 또는 감싸기 메서드 잔재 시: 해당 구문을 안전 삭제하여 소스 코드 경량화.

---

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: 전체 소스 코드 (`src/`, `scripts/`, `tests/`) 감사 및 하드코딩 제거율 100% 검증.
- **DoD-002**: `src/api`, `src/core`, `src/eval` 3대 계층 간 순환 참조 0건 및 계층적 모듈화 정립.
- **DoD-003**: 과도하게 복잡한 추상화 및 중복 코드 구문 단순화 리팩토링 완료.
- **DoD-004**: 전체 `pytest` 테스트 수트 (`uv run pytest -v`) 100% 통과 보장.
- **DoD-005**: 리팩토링 전후 기능적 사이드 이펙트(Side-effect) 발생 0건 검증.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (설정 단일 진실 소스 정립)**: 모든 모델 카탈로그 정보는 `config/model_catalog.json` 및 `ConfigManager`로 통일하고, 파이썬 파일 내 중복 딕셔너리 선언을 전면 제거해야 한다.
- **FR-002 (네트워크 및 VRAM 설정 외부화)**: 바인딩 포트(`8081`), 호스트, VRAM 상한선(`11264MB`), 헬스체크 타임아웃(`120s`)을 `config/server_config.json` 및 환경변수에서 로드해야 한다.
- **FR-003 (계층 간 단방향 의존성 준수)**: `src/api` (HTTP/Routing) -> `src/core` (Domain Logic) -> `src/eval` (Evaluation Engine) 순서의 명확한 단방향 계층 구조를 준수하고 상호 순환 참조를 금지해야 한다.
- **FR-004 (과도한 추상화 레이어 단순화)**: 가독성을 저해하는 3단계 이상의 래퍼 메서드 및 불필요한 프록시 함수는 1~2단계의 직관적인 클래스/메서드로 통합해야 한다.
- **FR-005 (중복 HTTP 클라이언트 인스턴스화 통합)**: `inference_api.py` 및 `benchmark_quality.py` 등에서 남발되는 HTTP 클라이언트 생성을 싱글톤 커넥션 풀로 일원화해야 한다.
- **FR-006 (타입 힌팅 및 독스트링 완비)**: 모든 핵심 클래스 및 메서드에 Python 3.12+ type hints 및 Google 스타일 Docstring을 작성해야 한다.
- **FR-007 (비파괴적 기능 보장)**: 리팩토링 과정에서 기존의 VRAM 100% 오프로딩 검증, 핫스왑, OpenAI API 규격 호환 기능이 100% 유지되어야 한다.
- **FR-008 (사설 내부망 IP 대역 접근제어 미들웨어)**: `0.0.0.0` 인터넷 전면 개방을 금지하고, `config/server_config.json`의 `allowed_subnets` (기본값 `["127.0.0.1", "192.168.0.0/24"]`) CIDR 필터 미들웨어를 적용하여 사설 내부망 접근만 허용해야 한다.
- **FR-009 (RAG 및 AI Agent 서비스 전용 고동시성 처리)**: RAG 파이프라인(긴 문서 컨텍스트) 및 AI Agent(스트리밍 토큰 생성) 마이크로서비스가 보낸 요청을 비동기 싱글톤 커넥션 풀로 지연 없이 수용해야 한다.

### Key Entities

- **ConfigRegistry**: `model_catalog.json` 및 `server_config.json`을 단일 진실 소스로 제공하는 설정 레지스트리 엔티티.
- **ModularLayerArchitecture**: API, Core, Eval 계층으로 직관되게 모듈화된 아키텍처 구조.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001 (하드코딩 제거율)**: 파이썬 소스 코드 내 포트, URL, 모델 카탈로그 하드코딩 잔재 0건 (100% 외부화).
- **SC-002 (순환 참조 0건)**: 계층 간 모듈 수입 시 순환 참조 발생 0건.
- **SC-003 (코드 가독성 및 단순성 향상)**: 불필요한 래퍼 함수 제거 및 복잡도 감소 완료.
- **SC-004 (테스트 패스율 100%)**: `uv run pytest -v` 수트 전체 통과률 100%.

---

## Assumptions

- 모든 설정 외부화는 `config/` 디렉터리 내 JSON 파일 및 `LLAMA_*` prefix 환경변수로 수용함.
- 기존 API 규격 (`GET /v1/models`, `POST /v1/chat/completions`) 및 CLI 스크립트 실행 양식은 100% 호환 유지됨.
