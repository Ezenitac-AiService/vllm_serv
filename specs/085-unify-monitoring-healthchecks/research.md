# Research: 서버 현황 모니터링 불일치 해소 및 헬스체크 통일

## 1. 대시보드(Port 8082) 프로브 타겟 및 옵션 통일

### Decision
`scripts/status_server.sh` 및 `scripts/diagnose_server_health.py`의 웹 대시보드 프로브 로직에 리다이렉트 추적(`-L` / `follow_redirects=True`), 타임아웃(`--max-time 5`), 및 다중 IP 탐색 후보(`127.0.0.1`, `localhost`, LAN IP)를 공통 적용한다.

### Rationale
기존 `status_server.sh`는 `http://127.0.0.1:8082/`에 대해 리다이렉션 미추적 및 LAN IP 탐색 실패 시 빈 문자열`""`을 리턴하여 오탐(`Port 8082 CLOSED`)을 기록하였다. `diagnose_server_health.py`와 동일하게 LAN IP 및 `-L` 옵션을 적용하면 오탐이 100% 해소된다.

---

## 2. 쉘 스크립트와 파이썬 진단 모듈 간 헬스 판정 통일

### Decision
`status_server.sh` 내부에서 헬스 검증 시 Python 헬퍼 또는 통합 curl 로직을 사용하여 포트 8081 `/health`, 포트 8082 `/`, 포트 8089/8090/8091 소켓 검증 결과를 직렬화하여 반환한다.

### Rationale
두 스크립트가 완전히 동일한 프로브 알고리즘을 사용함으로써 사용자에게 혼선을 일으키는 모순된 헬스 결과를 영구적으로 제거한다.
