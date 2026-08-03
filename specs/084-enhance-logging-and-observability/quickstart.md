# Quickstart Guide: 서버 진단 로그 강화 및 포트 정돈 검증

## 검증 시나리오 (Validation Scenarios)

### 시나리오 1: stop_server.sh 실행 후 잔존 포트 및 프로세스 클린 검증
```bash
./stop_server.sh
# 포트 8081, 8082, 8089, 8090, 8091 점유 PID가 0개인지 확인
lsof -i:8081 -i:8082 -i:8089 -i:8090 -i:8091 || echo "All ports cleanly released!"
```

### 시나리오 2: start_server.sh 실행 및 진단 헬스체크
```bash
./start_server.sh
uv run scripts/diagnose_server_health.py
# 결과: STATUS: 🎉 SYSTEM HEALTHY (/v1/chat/completions ✅ 200 OK)
```

### 시나리오 3: OpenAI 규격 대화 API 호출 검증
```bash
uv run samples/sample_01_chat.py
# 결과: ✅ [응답 성공]
```

### 시나리오 4: logs/error.log 정밀 로깅 검증
```bash
cat logs/error.log
# 결과: 단순 Status 503 문자열 외에 예외 원인 및 트레이스가 정상 포맷으로 기록되는지 확인
```
