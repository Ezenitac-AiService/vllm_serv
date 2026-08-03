# Data Model & State Schema: status_server.sh 대시보드 헬스체크

**Feature Short Name**: `fix-dashboard-status-healthcheck`  
**Target Directory**: `specs/087-fix-dashboard-status-healthcheck/`  
**Date**: 2026-08-03  

---

## 1. 대시보드 상태 진단 모델 (Dashboard Health Diagnostic State Model)

### 1.1 상태 분류 및 출력 매핑 (Status Enum & Terminal Output Mapping)

| 상태 코드 (State Code) | 검증 조건 (Verification Criteria) | 터미널 출력 메시지 (Terminal Output) |
|----------------------|-----------------------------------|------------------------------------|
| `RUNNING_VERIFIED` | 8082 소켓 개방 + HTTP 200/307 (Follow) 수신 + DOM 키워드 매칭 성공 (`vLLM\|Dashboard\|vllm_serv\|대시보드`) | `🟢 대시보드 서비스 및 HTML DOM 정상 작동 중 (Port 8082 OPEN, DOM Verified)` |
| `RUNNING_KEYWORD_MISSING` | 8082 소켓 개방 + HTTP 응답 수신되나 HTML DOM 키워드 미달 | `⚠️ 대시보드 포트 응답 수신되나 HTML DOM 키워드 검증 미달 (Port 8082 OPEN, Keyword Missing)` |
| `STOPPED_OR_CLOSED` | 8082 소켓 닫힘 또는 연결 거부(Connection Refused) | `⚪ 대시보드 미구동 또는 포트 차단됨 (Port 8082 CLOSED)` |

---

## 2. 프로브 순서 및 전이 (Probe Order & Transition Flow)

```mermaid
flowchart TD
    A[status_server.sh 실행] --> B{CURL_HOST 지정}
    B --> C[PROBE_HOSTS = 127.0.0.1, localhost, LAN_IP, SERVER_HOST]
    C --> D[curl -sL --max-time 3 http://HOST:8082/]
    D --> E{DASH_HTML 획득 여부}
    E -- 307 추적 및 HTML 수신 성공 --> F{grep -qE 'vLLM|Dashboard|vllm_serv|대시보드'}
    F -- 성공 --> G[RUNNING_VERIFIED: 🟢 Port 8082 OPEN, DOM Verified]
    F -- 실패 --> H[RUNNING_KEYWORD_MISSING: ⚠️ Port 8082 OPEN, Keyword Missing]
    E -- 획득 실패 (빈 본문) --> I[STOPPED_OR_CLOSED: ⚪ Port 8082 CLOSED]
```
