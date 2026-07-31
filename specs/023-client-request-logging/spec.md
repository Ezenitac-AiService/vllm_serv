# Feature Specification: 클라이언트 요청 트레이싱 및 상세 감사 로그 시스템 (023-client-request-logging)

**Feature Branch**: `023-client-request-logging`

**Created**: 2026-07-30

**Status**: Draft

**Input**: User request: "llm 서버들의 최신 로그 기록/관리 리서치, 클라이언트 식별 수단 확장, API Key 인가/마스킹 로깅, 웹 대시보드 UI 기반 API Key 생성·삭제 및 Admin Secret 관리자 인증 통합"

## Clarifications

### Session 2026-07-30

- Q: LiteLLM, Ollama, LM Studio, vLLM 등 최신 LLM 서버들의 로그 기록 및 관리 방식은 어떠한가? → A: LiteLLM 및 vLLM 프레임워크 표준에 따라 모든 HTTP 요청에 `X-Request-ID` (UUIDv4) 추적 헤더를 부여하고, 구조화된 Access Log(`logs/access.log`)와 Error Log(`logs/error.log`)로 분리 저장하며, `Client IP` (`X-Forwarded-For`), `Timestamp`, `Method/Path`, `Status Code`, `Latency (ms)`, `Requested Model`, `User-Agent`를 수록하고 10MB x 5개 파일 `RotatingFileHandler`로 디스크 용량을 자동 관리합니다.
- Q: OpenAI API 표준에서 API Key 외에 클라이언트를 식별할 수 있는 수단이 있는가? → A: OpenAI API 표준 규격상 API Key 헤더(`Authorization`) 외에도 1) 요청 페이로드 내 표준 `"user"` 필드 (예: `"user": "client-user-123"`), 2) 네트워크 레이어 `Client IP` (`X-Forwarded-For`), 3) `User-Agent` 헤더, 4) 커스텀 헤더(`X-Client-ID`, `X-User-ID`)가 존재합니다. 로깅 미들웨어는 해당 식별자들을 우선순위에 따라 추출하여 access.log 항목에 함께 수록합니다.
- Q: API Key를 이용한 인가 및 클라이언트 식별 기능 추가 시 범위는 어떠한가? → A: Option A(기본 API Key 검증 및 마스킹 로깅)를 채택합니다. `server_config.json`에 허용 API Key 목록(`api_keys`) 및 활성화 여부(`api_key_enabled`)를 정의하고, 미들웨어에서 `Authorization: Bearer <KEY>` 헤더를 검증하며, 마스킹된 Key(예: `sk-***key1`)를 `access.log` 및 `error.log` 항목에 함께 소요시간 없이 안전하게 기록합니다.
- Q: API Key 발급 기능 및 웹 UI 통합 여부는 어떠한가? → A: Option A(웹 UI + REST API/CLI)를 선택합니다. 기존 대시보드(`/dashboard`) 페이지에 "API Key 관리" UI 탭을 통합하여 웹 화면에서 클릭 한 번으로 API Key 생성, 클립보드 복사, 삭제를 수행할 수 있도록 하고 백엔드 관리 API (`/v1/admin/api-keys`) 및 쉘 CLI 커맨드를 함께 제공합니다.
- Q: 대시보드 및 Admin API 접근 인증 방식은 어떠한가? → A: Option A(Admin Secret / 비밀번호 기반 인증)를 채택합니다. `server_config.json` 또는 환경변수에 관리자 비밀번호(`admin_secret`)를 정의하며, `/dashboard` 대시보드 접속 모달 로그인 및 Admin REST API (`/v1/admin/*`) 호출 시 `X-Admin-Secret` 헤더 또는 관리자 세션 쿠키를 통한 인가를 필수로 검증합니다.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 클라이언트별 요청 및 엑세스 감사 로그 기록 (Priority: P1)

운영자가 LLM 서빙 중 장애 발생이나 특정 클라이언트의 오작동 요청을 분석하고자 할 때, 모든 HTTP 요청(엔드포인트: `/v1/chat/completions`, `/health` 등)의 클라이언트 IP, 시간, HTTP 메소드, 요청 경로, 응답 상태 코드, 소요 시간(ms), 요청 모델명, User-Agent, OpenAI `"user"` 필드 및 식별 헤더가 `logs/access.log`에 실시간으로 구체적으로 기록된다.

**Why this priority**: 클라이언트 식별 및 장애 추적을 위한 가장 기본적인 가시성(Observability) 제공 요구사항이다.

**Independent Test**: API 요청을 전송한 후 `logs/access.log` 파일에 클라이언트 IP, 식별자, 처리 시간이 정형화된 서식으로 기록되는지 확인한다.

**Acceptance Scenarios**:

1. **Given** 서빙 서버가 구동 중일 때, **When** 외부 클라이언트가 `/v1/chat/completions` 요청(페이로드에 `"user": "client-app-01"` 수록)을 보내면, **Then** `logs/access.log`에 `[TIMESTAMP] [CLIENT_IP] [REQUEST_ID] [user:client-app-01] POST /v1/chat/completions 200 OK - 150ms - model: qwen3.5-4b` 형식의 구조화된 로깅이 기록된다.

---

### User Story 2 - 요청 추적 ID (X-Request-ID) 발급 및 오류 원인 로그 기록 (Priority: P1)

운영자가 특정 문제 요청을 정밀하게 역추적할 때, 서버는 모든 요청에 고유한 추적 ID(`X-Request-ID`)를 부여하여 응답 헤더 및 로그에 수록하고, 4xx/5xx 예외 발생 시 에러 사유 및 트레이스백 요약을 `logs/error.log`에 원인과 함께 기록한다.

**Why this priority**: 문제 발생 클라이언트와 서버 측 처리 과정 간의 1:1 매핑을 통한 신속한 장애 진단을 가능하게 한다.

**Independent Test**: 잘못된 페이로드로 요청을 보낸 후 응답 헤더의 `X-Request-ID` 값으로 `logs/error.log`에서 해당 오류 내역을 조회 가능한지 확인한다.

**Acceptance Scenarios**:

1. **Given** 클라이언트의 잘못된 포맷 요청(400 Bad Request)이나 모델 처리 오류(500 Internal Server Error), **When** 오류 응답이 반환될 때, **Then** `X-Request-ID` 헤더가 응답에 포함되고 `logs/error.log`에 클라이언트 IP, 추적 ID, 오류 메시지가 기록된다.

---

### User Story 3 - 로그 파일 용량 관리 및 자동 로테이션 (Priority: P2)

운영자가 지속적인 서빙 환경을 운영할 때, 로그 파일이 디스크 용량을 전부 점유하지 않도록 크기 기반(예: 10MB 기준 백업 5개 retention) 자동 로테이션(Rotating File Handler)을 적용한다.

**Why this priority**: 장기간 서버 구동 시 로그 파일 비대로 인한 디스크 풀(Disk Full) 장애 방지.

**Independent Test**: 로테이션 설정을 검증하여 지정 크기 초과 시 `.log.1`, `.log.2` 백업 파일로 자동 분할되는지 확인한다.

**Acceptance Scenarios**:

1. **Given** `access.log` 및 `error.log` 크기가 지정된 임계값(예: 10MB)에 도달할 때, **When** 새로운 로그가 작성되면, **Then** 기존 파일이 로테이션되고 새 파일에 로깅이 이어서 작성된다.

---

### User Story 4 - API Key 기본 검증 및 마스킹 감사 로깅 (Priority: P2)

운영자가 허가된 클라이언트만 서빙에 접근하도록 제한하고자 할 때, `server_config.json`에 `api_key_enabled: true` 및 `api_keys` 목록을 설정하면 미들웨어가 `Authorization: Bearer <KEY>` 검증을 수행하고, 유효하지 않은 경우 401을 반환하며 감사 로그에는 마스킹된 키(예: `sk-***key1`)를 기록한다.

**Why this priority**: 최소한의 인증 및 보안 통제를 제공하면서 클라이언트 식별 가시성을 극대화한다.

**Independent Test**: 유효하지 않은 API Key로 요청 시 401 Unauthorized가 반환되고, 유효한 요청 시 마스킹된 Key 정보가 `access.log`에 기록되는지 확인한다.

**Acceptance Scenarios**:

1. **Given** `api_key_enabled: true` 설정 환경에서, **When** 클라이언트가 `Authorization: Bearer sk-valid-key1`을 전송하면, **Then** 200 OK 응답과 함께 `access.log`에 `key:sk-***key1` 정보가 기록된다.

---

### User Story 5 - 웹 대시보드 UI 및 REST API/CLI 기반 API Key 발급·관리 (Priority: P2)

운영자가 웹 대시보드 화면(`/dashboard`)에서 간편하게 API Key를 생성 및 관리하고자 할 때, "API Key 관리" UI 탭을 통해 신규 키 생성, 클립보드 복사, 키 목록 조회 및 삭제 작업을 직관적으로 수행할 수 있다.

**Why this priority**: 터미널 명령이나 JSON 파일 수동 수정 없이도 웹 환경에서 즉시 클라이언트 인가 키를 발급/관리하는 탁월한 운용 편의성 제공.

**Independent Test**: 브라우저에서 `/dashboard` 접속 후 API Key 관리 탭에서 `[새 API Key 발급]` 버튼을 클릭하여 키가 생성되고 `server_config.json`에 저장되는지 확인한다.

**Acceptance Scenarios**:

1. **Given** 운영자가 `/dashboard` 페이지에 접속해 있을 때, **When** API Key 관리 탭에서 키 이름을 입력하고 생성 버튼을 누르면, **Then** 새로운 `sk-vllm-...` 키가 발급되고 목록에 생성일시 및 마스킹 정보가 표시된다.

---

### User Story 6 - Admin Secret (관리자 비밀번호) 기반 대시보드 및 Admin API 인가 (Priority: P1)

외부 사용자의 무단 대시보드 접근 및 API Key 생성을 방지하고자 할 때, 관리자 비밀번호(`admin_secret`)를 검증하여 유효한 자격 증명이 확인된 경우에만 대시보드 접속 및 API Key 관리 API (`/v1/admin/*`) 호출을 허용한다.

**Why this priority**: 인가되지 않은 외부 사용자가 무단으로 API Key를 발급하거나 삭제하는 보안 사고 방지.

**Independent Test**: 올바르지 않은 비밀번호로 Admin API 호출 시 403 Forbidden / 401 Unauthorized가 반환되고, 올바른 비밀번호 인증 시 성공 응답을 반환하는지 확인한다.

**Acceptance Scenarios**:

1. **Given** `admin_secret`이 설정된 환경에서, **When** 관리자가 올바른 비밀번호를 입력하고 대시보드에 로그인하면, **Then** 대시보드 관리 기능 접속 및 API Key 발급 권한이 부여된다.

---

### Edge Cases

- 프록시/로드밸런서(Nginx, Cloudflare 등)를 경유할 때 `X-Forwarded-For` 헤더에서 실제 클라이언트 IP를 정상 추출할 수 있는가?
- 대량의 스트리밍 요청(SSE)이 유입될 때 로깅 미들웨어가 응답 지연을 유발하지 않는가?
- `api_key_enabled: false`인 경우 API Key 검증을 건너뛰고 비인증 로깅 모드로 정상 동작하는가?
- 올바르지 않은 `admin_secret`으로 Admin API 접근 시 403 Forbidden 응답이 반환되고 에러 로그에 시도 기록이 수록되는가?

## Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: FastAPI 미들웨어를 통해 모든 클라이언트 요청의 IP, 타임스탬프, 처리 시간, HTTP 메소드/경로, 상태 코드, OpenAI user 필드 및 클라이언트 식별 정보가 `logs/access.log`에 기록된다.
- **DoD-002**: 모든 요청 및 응답에 `X-Request-ID` 추적 헤더가 부여되고 `logs/error.log`에 4xx/5xx 상세 로그가 수록된다.
- **DoD-003**: `RotatingFileHandler`를 적용하여 로그 파일 자동 로테이션 및 용량 관리가 수행된다.
- **DoD-004**: `api_key_enabled` 옵션에 따라 Bearer 토큰 검증 및 마스킹 키 로깅이 정상 구동된다.
- **DoD-005**: `/dashboard` 웹 UI에 API Key 관리 인터페이스 및 백엔드 CRUD API가 구현된다.
- **DoD-006**: `admin_secret` 기반 관리자 인증 및 인가 보호가 적용된다.
- **DoD-007**: 로깅 및 키 관리 기능 단위/통합 테스트가 작성되고 전체 테스트 100% 통과한다.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: FastAPI 서버에 클라이언트 요청 및 감사 로깅 미들웨어(`ClientAccessLogMiddleware`)를 구현하여 클라이언트 IP(`X-Forwarded-For` 우선), 타임스탬프, HTTP 메소드, 요청 경로, 응답 상태 코드, 처리 시간(ms), User-Agent, 요청 모델명, OpenAI `"user"` 필드 및 `X-Client-ID` 식별자를 `logs/access.log`에 실시간으로 기록해야 한다 (MUST).
- **FR-002**: 모든 요청에 대해 UUIDv4 기반 `X-Request-ID` 추적 식별자를 생성하고, 응답 헤더 및 access/error 로그 항목에 결합하여 기록해야 한다 (MUST).
- **FR-003**: 4xx/5xx 오류 응답 발생 시 에러 발생 시간, 추적 ID, 클라이언트 IP, 예외 유형 및 에러 요약 메시지를 `logs/error.log` 파일에 기록해야 한다 (MUST).
- **FR-004**: 로그 핸들러에 `RotatingFileHandler`(최대 10MB, 백업 수 5개)를 적용하여 디스크 점유 폭증을 자동 방지해야 한다 (MUST).
- **FR-005**: 기존 REST API 및 OpenAI 호환 엔드포인트(`http://host:port/v1/chat/completions`)의 응답 속도 및 호환성에 영향을 주지 않아야 한다 (MUST).
- **FR-006**: `server_config.json` 설정에 따라 `api_key_enabled` 시 `Authorization: Bearer <KEY>` 인가를 수행하고, 마스킹 처리된 키(예: `sk-***key1`)를 감사 로그에 기록해야 한다 (MUST).
- **FR-007**: `/dashboard` 웹 대시보드 UI에 API Key 관리 탭/모달을 추가하여 `[키 생성]`, `[키 복사]`, `[키 삭제]` 인터페이스 및 관리용 REST API 엔드포인트 (`GET /v1/admin/api-keys`, `POST /v1/admin/api-keys`, `DELETE /v1/admin/api-keys`)를 제공해야 한다 (MUST).
- **FR-008**: Admin 대시보드(`/dashboard`) 접근 및 관리 REST API(`GET/POST/DELETE /v1/admin/api-keys`) 호출 시 `ADMIN_SECRET` (관리자 비밀번호) 헤더(`X-Admin-Secret`) 또는 세션 인증을 의무적으로 검증해야 한다 (MUST).

### Key Entities

- **Access Log Entry**: 클라이언트 IP, 추적 ID, 타임스탬프, 메소드, 경로, 상태코드, 지연시간, 모델명, User-Agent, OpenAI user 식별자, 마스킹된 API Key로 구성된 구조화 항목
- **Error Log Entry**: 추적 ID, 클라이언트 IP, 예외 클래스, 스택 트레이스 요약, 타임스탬프 정보
- **API Key Entry**: `key_id`, `name`, `masked_key`, `created_at`, `is_active` 데이터 모델

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 모든 API 요청에 대해 `X-Request-ID` 응답 헤더가 100% 포함된다.
- **SC-002**: API 요청 완료 후 `logs/access.log`에 1초 이내에 해당 엑세스 로그 항목이 기록된다.
- **SC-003**: 로깅 미들웨어 도입에 따른 요청 처리 지연 시간 추가 오버헤드가 2ms 이하로 유지된다.
- **SC-004**: 웹 대시보드(`/dashboard`)에서 API Key 생성 버튼 클릭 시 500ms 이내에 신규 키가 생성되어 화면 및 설정 파일에 저장된다.
- **SC-005**: 올바르지 않은 `admin_secret`으로 Admin API 호출 시 100% 403 Forbidden 응답으로 무단 접근을 차단한다.
- **SC-006**: 전체 pytest 테스트 수트 100% 통과를 유지한다.
