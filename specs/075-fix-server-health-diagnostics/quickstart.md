# Quickstart & Verification Guide: Server Health Diagnostics Fix

본 가이드는 Port 8082 대시보드 구동 및 `/v1/chat/completions` 진단 프로브가 100% HEALTHY(ALL GREEN) 상태로 수렴하는지 검증하는 가이드입니다.

---

## 1. 서버 재시작 및 멀티 포트 가동 실측 검증

```bash
# 1. 서버 프로세스 재구동
./stop_server.sh
./start_server.sh

# 2. 멀티 하드웨어 & 서버 포트 수신 리포트 확인
./status_server.sh
```

**기대 결과**:
- Port 8081 (LLM 메인) 및 Port 8082 (대시보드) 프로세스 상태가 정상 구동 중으로 표시됨.

---

## 2. 통합 진단 헬스체크 스크립트 실행 실측 검증

```bash
uv run python scripts/diagnose_server_health.py
```

**기대 결과 (Expected Outcome)**:
```text
====================================================
🔍 vllm_serv LLM 서버 통합 진단 및 헬스체크 보고서
====================================================
📡 감지된 유효 LAN IP : 127.0.1.1 (또는 설정 IP)
🤖 서빙 중인 LLM 모델  : ...

[방화벽 및 포트 개방 상태]
  - Port 8081_llm_main: ✅ OPEN
  - Port 8082_dashboard: ✅ OPEN

[API 엔드포인트 동작 상태]
  - /v1/models: ✅ 200 OK
  - /health: ✅ 200 OK
  - /v1/chat/completions: ✅ 200 OK

🖥️ 웹 대시보드 E2E 렌더링 : ✅ ON

STATUS: 🎉 SYSTEM HEALTHY
====================================================
```

---

## 3. 의무적 회귀 테스트 수트 실행 (헌법 VII조)

```bash
uv run pytest
```
