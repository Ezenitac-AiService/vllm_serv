# Research: 서비스 플랫폼 듀얼 랜 포트(Dual NIC) 192.168.0.x 서브넷 동적 인가 결정사항 (032-fix-internal-subnet-access)

## Research Topic 1: 듀얼 NIC 사설 IP 감지 및 CIDR 결합 메커니즘

### Decision
`src/api/server.py` 및 `src/core/config_manager.py`에서 허용 서브넷(`allowed_subnets`) 목록을 구성할 때 다음 결합 알고리즘을 적용한다:

```python
# 1. 정적 설정 파일 및 프로필 기본 대역
base_subnets = ["127.0.0.1", "192.168.0.0/16", "10.0.0.0/8", "172.16.0.0/12"]

# 2. NetworkDetector를 이용한 듀얼 NIC 활성 사설 IPv4 탐지
active_ips = NetworkDetector.get_active_lan_ips()

# 3. 실측 LAN IP 기반 서브넷 대역 동적 변환 및 합집합(Union)
dynamic_subnets = []
for ip in active_ips:
    if ip.startswith("192.168."):
        dynamic_subnets.append("192.168.0.0/16")
    elif ip.startswith("10."):
        dynamic_subnets.append("10.0.0.0/8")
    elif ip.startswith("172."):
        dynamic_subnets.append("172.16.0.0/12")
    else:
        # 기타 사설/내부 IP인 경우 /24 대역 자동 추출
        dynamic_subnets.append(f"{'.'.join(ip.split('.')[:3])}.0/24")

# 중복 제거된 최종 허용 서브넷 목록
allowed_subnets = list(dict.fromkeys(base_subnets + dynamic_subnets))
```

### Rationale
1. **듀얼 랜 포트 완벽 지원**: 랜 포트 1(`192.168.0.x`)과 랜 포트 2(`10.x.x.x` 등)가 동시에 활성화된 경우 두 포트의 IP가 모두 탐지되어 서브넷 대역이 합집합으로 결합됩니다.
2. **미사용/다운 포트 안전 스킵**: 케이블 미연결(Down) 또는 미할당(APIPA `169.254.x.x`) 포트는 `is_usable_lan` 필터링에 의해 자동으로 제외됩니다.
3. **정적/동적 2중 허용 보장**: 정적 설정 파일(`platform_profiles.json` 및 `server_config.json`)과 동적 감지(NetworkDetector)를 결합하여, 런타임 탐지 실패 시에도 기본 사설망 대역(`192.168.0.0/16`) 접근이 안전하게 통과됩니다.

### Alternatives Considered
- **정적 서브넷 대역만 수정**: 특정 프로필에서만 접속이 허용되고, 듀얼 NIC 중 다른 사설 대역 IP가 할당된 경우 차단되는 한계 존재 (기각).
- **모든 서브넷 전체 허용 (`0.0.0.0/0`)**: 공인 인터넷 IP로부터의 무분별한 포트 스캐닝 및 공격 위험이 발생하므로 보안 원칙상 기각.
