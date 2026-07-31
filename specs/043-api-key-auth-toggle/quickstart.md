# Quickstart Validation Guide (043-api-key-auth-toggle)

## Runnable Validation Scenarios

### Scenario 1: API 키 필수 토글 ON 및 HTTP 401 차단 실측
```bash
# 1. API 키 필수 인증 모드 활성화 (ON)
curl -X POST http://127.0.0.1:8081/dashboard/api/config \
  -H "Content-Type: application/json" \
  -d '{"api_key_enabled": true}'

# 2. 헤더 없이 인퍼런스 요청 -> HTTP 401 Unauthorized 기대
curl -i http://127.0.0.1:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen3.5-4b","messages":[{"role":"user","content":"hi"}]}'
# Expected Output: HTTP/1.1 401 Unauthorized
```

### Scenario 2: 유효한 API 키 헤더 포함 호출 및 SQLite 메트릭 축적 확인
```bash
# 유효 키 헤더 포함 호출 -> HTTP 200 OK
curl -i http://127.0.0.1:8081/v1/chat/completions \
  -H "Authorization: Bearer sk-vllm-test" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen3.5-4b","messages":[{"role":"user","content":"hi"}]}'

# 메트릭 SQL 집계 확인
curl http://127.0.0.1:8081/dashboard/api/keys/metrics
```

### Scenario 3: 단위 및 통합 테스트 실행
```bash
uv run pytest tests/unit/test_api_key_auth_toggle.py -v
```
