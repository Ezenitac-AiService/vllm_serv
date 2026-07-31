# API Contracts: API Key 관리 및 Admin 인증 엔드포인트 (023-client-request-logging)

## 1. 관리자 로그인 (`POST /v1/admin/auth/login`)

관리자 비밀번호를 검증하여 관리자 세션 쿠키 또는 토큰을 발급받습니다.

### Request Headers
- `Content-Type: application/json`

### Request Body
```json
{
  "admin_secret": "my-secure-admin-password"
}
```

### Response Success (`200 OK`)
```json
{
  "status": "success",
  "session_token": "admin-sess-8a7b6c5d4e3f...",
  "message": "Admin authenticated successfully"
}
```

### Response Error (`401 Unauthorized`)
```json
{
  "detail": "Invalid admin secret"
}
```

---

## 2. API Key 목록 조회 (`GET /v1/admin/api-keys`)

등록된 모든 API Key의 마스킹 목록 및 상태 정보를 조회합니다.

### Request Headers
- `X-Admin-Secret: my-secure-admin-password` (또는 Cookie: `admin_session=...`)

### Response Success (`200 OK`)
```json
{
  "status": "success",
  "api_keys": [
    {
      "key_id": "key-uuid-1111",
      "name": "Production Client A",
      "masked_key": "sk-***8f9a",
      "created_at": "2026-07-30T05:30:00Z",
      "is_active": true
    }
  ]
}
```

---

## 3. 신규 API Key 발급 (`POST /v1/admin/api-keys`)

새로운 API Key를 생성하여 발급합니다. **(생성 시 1회에 한해 raw `raw_api_key` 반환)**

### Request Headers
- `X-Admin-Secret: my-secure-admin-password`
- `Content-Type: application/json`

### Request Body
```json
{
  "name": "Marketing-Bot-Key"
}
```

### Response Success (`201 Created`)
```json
{
  "status": "created",
  "key_id": "key-uuid-2222",
  "name": "Marketing-Bot-Key",
  "raw_api_key": "sk-vllm-7c89f0a1b2c3d4e5f6g7h8i9j0",
  "masked_key": "sk-***i9j0",
  "created_at": "2026-07-30T05:40:00Z",
  "warning": "This raw API key will only be shown ONCE. Please store it securely."
}
```

---

## 4. API Key 삭제/폐기 (`DELETE /v1/admin/api-keys/{key_id}`)

특정 API Key를 즉시 폐기/삭제합니다.

### Request Headers
- `X-Admin-Secret: my-secure-admin-password`

### Response Success (`200 OK`)
```json
{
  "status": "deleted",
  "key_id": "key-uuid-2222",
  "message": "API key revoked successfully"
}
```
