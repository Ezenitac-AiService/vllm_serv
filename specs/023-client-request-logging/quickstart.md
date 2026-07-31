# Quickstart & Verification Guide: 클라이언트 요청 트레이싱 및 상세 감사 로그 시스템 (023-client-request-logging)

본 가이드는 클라이언트 요청 트레이싱 및 상세 감사 로그 시스템(`023-client-request-logging`)의 작동을 검증하는 실행 절차를 제공합니다.

---

## 1. 사전 준비 및 단위 테스트 실행

```bash
# 로깅 및 키 관리 단위 테스트 실행
uv run pytest tests/unit/test_client_access_logger.py
uv run pytest tests/unit/test_api_key_manager.py
```

---

## 2. API Key 발급 및 로그인 검증 시나리오

### 시나리오 A: 관리자 대시보드 로그인 및 API Key 생성
1. 서빙 서버 구동:
   ```bash
   ./start_server.sh
   ```
2. 웹 브라우저 접속: `http://localhost:8081/dashboard`
3. 관리자 비밀번호 로그인 창에서 설정된 `admin_secret` 입력 후 접속.
4. "API Key 관리" 탭 이동 → `[새 API Key 생성]` 클릭 → 이름("Test-Client") 입력.
5. 발급된 `sk-vllm-...` 키 클립보드 복사.

### 시나리오 B: API Key 인가 및 `access.log` 기록 검증
1. 발급받은 API Key로 `/v1/chat/completions` API 요청 전송:
   ```bash
   curl -X POST http://localhost:8081/v1/chat/completions \
     -H "Authorization: Bearer sk-vllm-your-generated-key" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "qwen3.5-4b",
       "messages": [{"role": "user", "content": "Hello!"}],
       "user": "quickstart-client-01"
     }'
   ```
2. 응답 헤더 확인:
   - `X-Request-ID: req-XXXX...` 포함 여부 검증.

3. `logs/access.log` 확인:
   ```bash
   tail -n 5 logs/access.log
   ```
   **기동 결과 검증**: `[CLIENT_IP] [req-XXXX] [key:sk-***key] [user:quickstart-client-01] POST /v1/chat/completions 200 OK` 항목 확인.

### 시나리오 C: 에러 감사 로그 (`logs/error.log`) 및 401 차단 검증
1. 유효하지 않은 API Key로 요청:
   ```bash
   curl -X POST http://localhost:8081/v1/chat/completions \
     -H "Authorization: Bearer sk-invalid-key" \
     -H "Content-Type: application/json" \
     -d '{"model": "invalid-model"}'
   ```
2. HTTP 401 또는 404 응답 확인.
3. `logs/error.log` 파일에 실패 요청 트레이스 기록 확인:
   ```bash
   tail -n 5 logs/error.log
   ```
