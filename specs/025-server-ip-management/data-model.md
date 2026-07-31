# Data Model: 듀얼 랜포트 다중 NIC 환경 서버 IP 바인딩 및 네트워크 관리 로직 고도화 (025-server-ip-management)

## Entities

### 1. NetworkInterfaceInfo (네트워크 인터페이스 엔티티)

서버 메인보드에 탑재된 개별 물리/논리 네트워크 카드(NIC)의 상태 정보 데이터 모델입니다.

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `name` | String | Non-empty | 인터페이스 이름 (예: `eth0`, `eno1`, `wlan0`) |
| `ip_address` | String | Optional IPv4 | 할당된 IPv4 주소 (미할당 포트 시 `None`) |
| `is_active` | Boolean | Required | 인터페이스 활성화 및 Link Up 여부 |
| `is_loopback` | Boolean | Required | 루프백 인터페이스(`127.0.0.1`) 여부 |
| `is_usable_lan` | Boolean | Required | 외부 LAN 접속 수용 가능한 유효 사설/공공 IP 여부 |

---

### 2. ServerNetworkConfig (서버 네트워크 관리 구성 엔티티)

서버 파이프라인 엔진 전체의 소켓 바인딩, 서브넷 필터, 방화벽 관리 구성 명세 데이터 모델입니다.

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `bind_host` | String | Default `"0.0.0.0"` | API 서버 및 LLM 하위 프로세스 호스트 바인딩 주소 |
| `api_port` | Integer | 1-65535, Default `8081` | vLLM / llama FastAPI 서빙 포트 |
| `llama_server_port` | Integer | 1-65535, Default `8089` | llama-server C++ 바이너리 전용 포트 |
| `allowed_subnets` | List[String] | CIDR notation | 접근 허용 서브넷 목록 (예: `["127.0.0.1/32", "192.168.0.0/16"]`) |
| `detected_active_ips` | List[String] | IPv4 list | 감지된 유효 활성 LAN IP 주소 목록 |
| `firewall_auto_allow` | Boolean | Default `true` | OS 방화벽(`ufw`) 포트 개방 자동 시도 여부 |

---

### 3. FirewallStatusInfo (OS 방화벽 상태 및 진단 엔티티)

OS 레벨 방화벽 상태 및 포트 개방 시도 결과 진단 모델입니다.

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `system_type` | String | Enum (`ufw`, `iptables`, `firewalld`, `unknown`) | 감지된 OS 방화벽 관리 시스템 |
| `is_firewall_active` | Boolean | Required | OS 방화벽 작동 여부 |
| `port_open_success` | Boolean | Required | 대상 포트 개방 성공 여부 |
| `requires_sudo` | Boolean | Required | sudo 권한 부족으로 실패했는지 여부 |
| `guide_message` | String | Non-empty | 권한 부족 시 사용자에게 제공되는 수동 개방 명령 가이드 |
