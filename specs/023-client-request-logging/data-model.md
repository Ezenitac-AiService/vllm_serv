# Data Model & Schema Specifications: 클라이언트 요청 트레이싱 및 상세 감사 로그 시스템 (023-client-request-logging)

## Entities & Schemas

### 1. `AccessLogEntry`

FastAPI 미들웨어에서 수집되어 `logs/access.log`에 기록되는 엑세스 감사 로그 데이터 구조.

```python
class AccessLogEntry(BaseModel):
    timestamp: str  # ISO 8601 UTC 타임스탬프 (예: "2026-07-30T05:30:00Z")
    client_ip: str  # X-Forwarded-For 또는 socket host
    request_id: str  # UUIDv4 추적 식별자 (예: "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d")
    method: str  # HTTP 메소드 (GET, POST 등)
    path: str  # 요청 엔드포인트 경로 (예: "/v1/chat/completions")
    status_code: int  # HTTP 응답 상태 코드 (200, 400, 401, 500 등)
    latency_ms: float  # 요청 처리 소요 시간 (밀리초)
    model: Optional[str] = None  # 요청에 포함된 LLM 모델명
    openai_user: Optional[str] = None  # OpenAI payload "user" 필드값
    masked_api_key: Optional[str] = None  # 마스킹 처리된 API 키 (예: "sk-***key1")
    user_agent: Optional[str] = None  # User-Agent 헤더
```

**Log Format (String Output)**:
`[2026-07-30T05:30:00Z] [192.168.1.50] [req-9b1deb4d] [key:sk-***key1] [user:app-01] POST /v1/chat/completions 200 OK - 145.2ms - model: qwen3.5-4b`

---

### 2. `ErrorLogEntry`

4xx/5xx 예외 발생 시 `logs/error.log`에 기록되는 에러 상세 감사 로그 데이터 구조.

```python
class ErrorLogEntry(BaseModel):
    timestamp: str  # ISO 8601 UTC 타임스탬프
    request_id: str  # UUIDv4 추적 식별자
    client_ip: str  # 클라이언트 IP
    path: str  # 요청 엔드포인트 경로
    status_code: int  # HTTP 상태 코드 (4xx/5xx)
    exception_type: str  # 발생한 예외 클래스명 (예: "HTTPException", "ValueError")
    error_detail: str  # 에러 요약 메시지
    masked_api_key: Optional[str] = None  # 사용된 마스킹 키
    traceback_summary: Optional[str] = None  # 스택트레이스 요약
```

---

### 3. `ApiKeyEntity`

`server_config.json` 및 메모리에 저장되는 API Key 관리 엔티티.

```python
class ApiKeyEntity(BaseModel):
    key_id: str  # Key 고유 ID (UUIDv4)
    name: str  # 키 식별 이름 (예: "Marketing-Bot-Key")
    hashed_key: str  # SHA-256 해시 문자열
    masked_key: str  # 화면 표시용 마스킹 문자열 (예: "sk-***8f9a")
    created_at: str  # 생성 타임스탬프
    is_active: bool = True  # 키 활성화 여부
```

---

### 4. `AdminSessionState`

웹 대시보드 및 REST API 인증을 관리하는 데이터 구조.

```python
class AdminSessionState(BaseModel):
    admin_secret_hash: str  # 설정된 관리자 비밀번호 SHA-256 해시
    session_tokens: Dict[str, str] = Field(default_factory=dict)  # token -> created_at
```
