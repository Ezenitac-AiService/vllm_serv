# Data Model: LLM 서버 통합 진단 리포트 (072-server-e2e-health-check)

## Entity: `ServerHealthReport`

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `detected_lan_ip` | `string` | 감지된 유효 LAN IP (예: 10.0.0.15 또는 192.168.0.100) |
| `served_models` | `List[string]` | `/v1/models` API에서 반환된 서비스 중인 모델명 목록 |
| `api_status` | `Dict[string, bool]` | 각 엔드포인트별(`models`, `chat/completions`, `health`) 응답 여부 |
| `firewall_ports` | `Dict[int, bool]` | 각 포트별(8081, 8082) 방화벽 허용 및 바인딩 상태 |
| `dashboard_e2e_status` | `bool` | 웹 대시보드 브라우저 렌더링 E2E 테스트 성공 여부 |
| `is_healthy` | `bool` | 전체 서버 통합 건강 상태 통과 여부 |
