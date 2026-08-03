# Research & Technical Decisions: `076-fix-service-platform-parity`

## 1. Loopback Multi-IP Probing Strategy
- **Decision**: `127.0.0.1`, `localhost`, `127.0.1.1`, active LAN IP 순회 탐색.
- **Rationale**: 서비스 플랫폼 리눅스의 `/etc/hosts` 설정으로 인해 `NetworkDetector`가 `127.0.1.1`을 감지할 때, Uvicorn 바인딩 주소와의 차이로 인한 Connection Refused 오탐을 완벽히 소멸시킴.

## 2. One-Stop Daemon Readiness Check & Atomic Rollback
- **Decision**: `start_server.sh` 구동 시 Port 8081 메인 API 및 Port 8082 대시보드의 Readiness(최대 30초)를 동시 검증하고, 하나라도 미응답 시 PID 원자적 Clean Exit/Rollback 수행.
- **Rationale**: 8081만 켜지고 8082가 튕기는 반쪽짜리 좀비 데몬 생성을 원천 차단.

## 3. HTML DOM Content Verification for Zero False Positive
- **Decision**: `check_dashboard_e2e()`에서 단순 HTTP 200/307 상태 코드 확인 외에 HTML 본문 내 `vllm_serv` / `Dashboard` 키워드 포함 여부 실측 검증.
- **Rationale**: HTTP 500 에러 페이지나 빈 화면이 리턴될 때 대시보드가 정상 가동 중이라고 잘못 판단하는 허위 양성(False Positive) 차단.

## 4. Mandatory Executable Permission & Multi-OS Firewall Enforcer
- **Decision**: `setup.sh` 완결 단계에서 `chmod +x`를 스크립트 전역 및 루트 심볼릭 링크에 재강제 적용하고 UFW `8081/tcp`, `8082/tcp` 원스톱 승인.
- **Rationale**: 이관 배포 후 Permission Denied 및 방화벽 차단 사고 물리적 근절.
