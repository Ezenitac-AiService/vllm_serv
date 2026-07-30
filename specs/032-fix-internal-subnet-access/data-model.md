# Data Model: 듀얼 NIC 서브넷 인가 및 동적 네트워크 엔티티 (032-fix-internal-subnet-access)

## Entities

### 1. DynamicSubnetGuard (엔티티)

`IpSubnetGuard` 클래스 기반 런타임 클라이언트 서브넷 인가 엔진.

| Attribute | Type | Description |
|-----------|------|-------------|
| `networks` | `list[ipaddress.IPv4Network]` | 파싱된 허용 CIDR 대역 네트워크 객체 목록 |
| `base_subnets` | `list[string]` | `["127.0.0.1", "192.168.0.0/16", "10.0.0.0/8", "172.16.0.0/12"]` |
| `detected_active_ips` | `list[string]` | `NetworkDetector`에서 스캔한 활성 LAN IPv4 주소 목록 |
| `union_allowed_subnets` | `list[string]` | 정적 기본 대역과 실측 감지 CIDR의 중복 제거 합집합 |

---

## Data Flow & Request Filtering Sequence

```mermaid
sequenceDiagram
    autonumber
    actor Client as 192.168.0.x Client
    participant Server as FastAPI Server
    participant Detector as NetworkDetector
    participant Guard as SubnetFilterMiddleware
    
    Server->>Detector: get_active_lan_ips() (Dual NIC 스캔)
    Detector-->>Server: ["192.168.0.15", "10.0.1.20"]
    Server->>Guard: allowed_subnets 합집합 생성 ("192.168.0.0/16", "10.0.0.0/8")
    
    Client->>Guard: HTTP Request (Client IP: 192.168.0.100)
    Guard->>Guard: is_allowed("192.168.0.100") 검증
    Guard-->>Client: HTTP 200 OK (허용 통과)
```
