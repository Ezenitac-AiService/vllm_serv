# Data Model: 서버 방화벽 구축 파이프라인 전수 검토 및 E2E 실측 테스트 (038-server-firewall-setup-pipeline)

## Core Entities & Schemas

### 1. `FirewallDiagnosticReport` (OS 방화벽 진단 보고서 객체)

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `system_type` | `str` | OS 방화벽 관리 유틸리티 (`"ufw"`, `"firewalld"`, `"iptables"`) | `"ufw"` |
| `is_firewall_active` | `bool` | 커널 방화벽 활성화 상태 | `true` |
| `target_port` | `int` | 검증 대상 서빙 포트 | `8081` |
| `is_port_allowed` | `bool` | 방화벽 룰셋에 허용 등록 여부 | `true` |
| `requires_sudo` | `bool` | 포트 개방을 위해 sudo 비밀번호 입력 필요 여부 | `false` |
| `is_tty_interactive` | `bool` | 실행 터미널의 대화형 TTY 보유 여부 | `true` |
| `guide_command` | `str` | 권한 부족 시 사용자가 복구할 터미널 수동 명령 | `"sudo ufw allow 8081/tcp"` |

---

### 2. `RealSocketConnectivityResult` (실물 IP 소켓 연결 실측 객체)

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `target_host` | `str` | 검증 대상 서버 실물 IP 주소 | `"10.0.0.41"` |
| `target_port` | `int` | 검증 대상 서빙 포트 | `8081` |
| `socket_connected` | `bool` | 물리 TCP 소켓 핸드셰이크 성공 여부 | `true` |
| `rtt_ms` | `float` | 소켓 연결 왕복 지연시간 (ms) | `2.4` |
| `error_detail` | `Optional[str]` | 연결 실패 시 소켓 에러 메시지 | `null` |

---

### 3. `E2EPageUsabilityResult` (Playwright E2E UI/UX 실측 객체)

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `url` | `str` | Playwright 진입 실물 IP 주소 | `"http://10.0.0.41:8081/dashboard/"` |
| `http_status` | `int` | 대시보드 메인 페이지 HTTP 응답 코드 | `200` |
| `dom_loaded` | `bool` | DOM 및 4대 탭 UI 렌더링 완료 여부 | `true` |
| `tabs_clickable` | `bool` | 4대 탭 (모니터링, 제어, 플레이그라운드, 감사) 클릭 전환 정상 동작 | `true` |
| `capabilities_loaded` | `bool` | `/dashboard/api/capabilities` 동적 모델 로딩 성공 여부 | `true` |
