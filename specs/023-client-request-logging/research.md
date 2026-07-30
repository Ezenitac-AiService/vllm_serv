# Technical Research & Architecture Decisions: 클라이언트 요청 트레이싱 및 상세 감사 로그 시스템 (023-client-request-logging)

## Research Questions & Decisions

### 1. 비동기 큐 기반 로깅 (Non-blocking Asynchronous Logging)

- **Problem**: Python의 표준 `logging.handlers.RotatingFileHandler`는 디스크 동기 쓰기(Blocking I/O)를 수행하므로 대량의 RPS 유입 시 Uvicorn 이벤트 루프를 차단하여 HTTP 지연을 유발함.
- **Decision**: Python `logging.handlers.QueueHandler`와 `QueueListener` 패턴을 도입하여 HTTP 미들웨어에서는 로그 이벤트를 메모리 큐에 보낸 후 2ms 이내 즉시 응답을 완료하고, 백그라운드 스레드에서 파일 쓰기 및 로테이션을 처리함.
- **Alternatives Considered**:
  - *동기 로깅*: 초당 요청 수 증가 시 이벤트 루프 대기로 서버 응답 속도 수십 ms 저하.
  - *Celery / Redis 비동기 타사 MQ*: 외부 종속성 추가로 온프레미스/단일 노드 구축 복잡성 가중.

### 2. API Key 보안 및 SHA-256 해시 저장

- **Problem**: API Key 원본을 `server_config.json`이나 파일에 평문 저장할 경우 파일 유출 시 모든 클라이언트 접근 권한이 상실/탈취됨.
- **Decision**:
  - API Key 생성 시 원본 `sk-vllm-XXXX...` 키는 웹 UI 발급 시점에 **오직 1회만 화면에 노출**.
  - 디스크 저장소에는 `SHA-256` 해시값(`hashed_key`) 및 마스킹 키(`sk-***<last_4>`), 생성일시, 활성화 여부만 저장.
  - API 요청 검증 시 클라이언트가 전송한 Bearer 토큰의 SHA-256 해시를 비교하여 인가 수행.
  - `access.log` 및 `error.log` 항목에는 마스킹된 키(`sk-***key1`)만 노출.

### 3. Admin Secret 관리자 인증 및 인가 보호

- **Problem**: `/dashboard` 웹 UI 및 `/v1/admin/*` API Key 관리 엔드포인트에 대한 무단 접근 및 키 발급/삭제 예방.
- **Decision**:
  - `server_config.json` 또는 환경변수 `VLLM_ADMIN_SECRET`을 통해 관리자 비밀번호 관리.
  - 대시보드 UI 접속 시 비밀번호 입력 폼 모달 제공 및 세션 쿠키 저장.
  - Admin REST API (`/v1/admin/api-keys`) 호출 시 `X-Admin-Secret` 헤더 또는 관리자 세션 검증 (실패 시 403 Forbidden 반환).

### 4. 클라이언트 식별 정보 (Identity) 다각화 수집

- **Problem**: OpenAI API 규격상 클라이언트별 식별 수단이 다양하여 단일 헤더 추출만으로는 정밀한 역추적이 어려움.
- **Decision**:
  - `ClientAccessLogMiddleware`에서 다음 순서로 클라이언트 식별자를 종합 추출하여 `access.log`에 결합 기록:
    1. `Client IP`: `X-Forwarded-For` 헤더 (프록시 경유 시) 또는 `request.client.host`
    2. `User-Agent`: 요청 HTTP User-Agent 헤더
    3. `API Key Mask`: Authorization Bearer 키의 마스킹 표기
    4. `OpenAI User`: JSON Payload의 `"user"` 필드 (존재 시)
    5. `Custom Header`: `X-Client-ID` / `X-User-ID` (존재 시)
