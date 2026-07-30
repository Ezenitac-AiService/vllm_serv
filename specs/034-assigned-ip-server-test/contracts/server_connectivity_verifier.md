# Contract Specification: `ServerConnectivityVerifier` Interface

## Component Overview

`ServerConnectivityVerifier`는 서버 구동 확인 시 `127.0.0.1` 루프백 인터페이스 및 시스템에 할당된 모든 비-루프백 LAN IP(듀얼랜 포함)에 대한 접속, API 호출 및 응답 정합성을 검증하는 파이썬 모듈 인터페이스입니다.

## Python API Contract

```python
class ServerConnectivityVerifier:
    """Verifies server responsiveness across localhost and all assigned network IP addresses."""

    def __init__(self, port: int = 8081, endpoint: str = "/health", timeout: float = 3.0):
        """Initializes verifier with target port, endpoint path, and request timeout."""
        ...

    def get_target_ips(self) -> List[str]:
        """Returns loopback IP ('127.0.0.1') + all active LAN IPs detected by NetworkDetector."""
        ...

    def verify_ip(self, ip_address: str) -> IPTestVerdict:
        """Attempts HTTP GET connection and request to target IP address.
        
        Returns:
            IPTestVerdict with status, http_status_code, response_time_ms, and error_message.
        """
        ...

    def verify_all(self) -> ConnectivityReport:
        """Executes verification for all target IPs and returns aggregated ConnectivityReport."""
        ...
```

## Expected Behavior & Edge Cases

1. **정상 동작**:
   - `verify_all()` 실행 시 `127.0.0.1` 및 `NetworkDetector.get_active_lan_ips()`로 감지된 모든 IP(예: `192.168.1.10`, `10.0.0.5`)에 대하여 HTTP GET 요청을 보낸다.
   - 모든 IP에서 HTTP 200 OK 수신 시 `ConnectivityReport.all_passed == True`.

2. **접속 실패 / 바인딩 제한**:
   - 서버가 `127.0.0.1`로만 바인딩되어 외부 LAN IP 접속 시 Connection Refused 발생 시:
     - `IPTestVerdict.status = "CONNECTION_REFUSED"`
     - `ConnectivityReport.all_passed = False`
     - `ConnectivityReport.failed_ips`에 실패 IP 명시 및 진단 메시지 저장.

3. **네트워크 미연결 단독 환경**:
   - 활성 비-루프백 IP가 존재하지 않는 경우:
     - `get_target_ips()`는 `["127.0.0.1"]`을 반환하며 루프백 검증 수행 후 적절한 경고 알림 포함.
