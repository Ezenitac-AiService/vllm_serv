# Research Report: status_server.sh 대시보드 헬스체크 307 리다이렉트 처리 및 상태 진단 정확도 정상화

**Feature Short Name**: `fix-dashboard-status-healthcheck`  
**Target Directory**: `specs/087-fix-dashboard-status-healthcheck/`  
**Date**: 2026-08-03  

---

## 1. 307 Temporary Redirect 및 대시보드 헬스체크 메커니즘 분석

### Decision 1: curl -sL 옵션 적용 및 /dashboard/ 보조 프로브
- **선택된 방안**: `scripts/status_server.sh`의 대시보드 curl 탐색 시 `curl -sL --max-time 3 "http://$CURL_HOST:8082/"` 및 `/dashboard/` 경로 직접 조회를 병행함.
- **선택 사유**:
  - FastAPI/Starlette Uvicorn 서버는 `/` 접근 시 `/dashboard/` 경로로 `307 Temporary Redirect` (Location: `/dashboard/`, 본문 0바이트)를 반환함.
  - `-L` (Location Follow) 플래그를 추가하면 curl이 307 리다이렉트를 추적하여 최종 HTML DOM (키워드: `vLLM|Dashboard|vllm_serv|대시보드`)을 획득함.
- **비교 및 기각된 대안**:
  - 대안 A: 루트 `/` 경로를 누르고 `/dashboard/` 경로만 단독 조회. -> 기존 `/` 접근 호환성이 상실될 수 있으므로 `-L`을 기본으로 하되 `/dashboard/`를 보완으로 사용하는 결합 방식 채택.

### Decision 2: 다중 루프백 IP 바인딩 탐색 (Probe Order)
- **선택된 방안**: `SERVER_HOST`가 `0.0.0.0`일 경우 `PROBE_HOSTS=("127.0.0.1" "localhost" "$LAN_IP")` 순서로 헬스체크 탐색을 수행함.
- **선택 사유**: OS 네트워크 카드 바인딩 환경 및 IPv4/IPv6 설정 차이에 의해 `127.0.0.1` 또는 `localhost` 중 하나만 소켓 개방을 응답할 때도 헬스체크 거짓 음성을 원천 방지함.

### Decision 3: 통합 회귀 테스트 수트 보장
- **선택된 방안**: `tests/integration/test_server_health_diagnostics_consistency.py`에 `status_server.sh` 헬스체크 출력과 `diagnose_server_health.py` 진단 간의 결과 일치성 단동 검증 테스트 포함.
- **선택 사유**: 헌법 VII조(의무적 회귀 테스트) 준수 및 이후 스크립트 변경 시 동일 오진 재발 방지.
