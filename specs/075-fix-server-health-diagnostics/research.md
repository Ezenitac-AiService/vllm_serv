# Technical Research: 서버 헬스진단 및 8082 대시보드 복구 (075-fix-server-health-diagnostics)

## Overview & Technical Context

배포 환경 진단 시 발견된 Port 8082 대시보드 차단/미구동(CLOSED/BLOCKED) 및 `/v1/chat/completions` 프로브 미도달(UNREACHABLE) 문제의 원인을 기술적으로 분석하고 최적의 해결 방안을 결정합니다.

---

## Key Decisions

### Decision 1: Port 8082 웹 대시보드 자동 프로세스 연동 및 방화벽 등록

- **Decision**: `./start_server.sh` 가동 시 FastAPI 기반 대시보드 모듈(또는 대시보드 렌더러) 프로세스를 Port 8082에 원스톱으로 자동 생성하고, `scripts/setup.sh`에 `ufw allow 8082/tcp` 방화벽 규칙을 수록합니다.
- **Rationale**: 서버 구동 시 사용자가 수동으로 대시보드를 켜지 않아도 진단 툴 및 외부에서 대시보드 E2E가 ✅ OPEN / ✅ ON 상태로 즉시 조회됩니다.
- **Alternatives Considered**: 별도의 `start_dashboard.sh`로 분리 (운영 인지 부하 증가 및 수동 누락 위험으로 기각).

### Decision 2: `scripts/diagnose_server_health.py` 내 `/v1/chat/completions` 프로브 파이썬 dict 기반 리팩토링

- **Decision**: `diagnose_server_health.py`의 대화 프로브 호출 시 Pydantic 의존성 없이 표준 파이썬 dict (`{"model": "qwen3.5-4b", "messages": [{"role": "user", "content": "ping"}], "max_tokens": 10}`) 페이로드를 사용하고, 타임아웃 10초 및 소켓 예외를 안전하게 처리합니다.
- **Rationale**: Pydantic 스키마 잔재나 바인딩 IP 불일치로 인한 false positive (UNREACHABLE) 경고를 없애고 200 OK 수신을 정밀 검증합니다.
- **Alternatives Considered**: 단순 TCP 포트 소켓 오픈 체크만 수행 (실제 LLM 추론 가능 여부를 검증하지 못하므로 기각).

---

## Verification Strategy

1. `./start_server.sh` 구동 후 `./status_server.sh` 실행 시 Port 8081 및 Port 8082 헬스 상태가 정상 표시됨을 확인.
2. `python scripts/diagnose_server_health.py` 실행 시 모든 엔드포인트 및 방화벽/대시보드가 ✅ OPEN / ✅ 200 OK / ✅ ON (STATUS: 🎉 SYSTEM HEALTHY)로 출력됨을 실측 검증.
