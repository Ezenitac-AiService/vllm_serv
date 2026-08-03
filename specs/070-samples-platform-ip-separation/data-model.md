# Data Model: samples 예제 스크립트의 서비스 플랫폼 IP 대역 접속 보장 및 테스트 스크립트 실 IP 검증 분리 (070-samples-platform-ip-separation)

## Client Configuration Schema (`samples/config.json`)

훈련생 및 외부 연동 사용자가 서비스 플랫폼(`192.168.0.x`) 서버 접속 주소 및 포트를 정의하는 설정 스키마입니다.

### Entity: `SampleClientConfig`

| Field Name | Type | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `server_host` | `string` | `"http://192.168.0.100"` | 접속 대상 서비스 플랫폼 IP 또는 도메인 URL |
| `main_port` | `integer` | `8081` | LLM 메인 차트 및 Completions API 포트 |
| `embedding_port` | `integer` | `8090` | BGE M3 임베딩 전용 API 포트 |
| `rerank_port` | `integer` | `8091` | BGE Reranker 전용 API 포트 |

#### JSON Example (`samples/config.json.example`)
```json
{
  "server_host": "http://192.168.0.100",
  "main_port": 8081,
  "embedding_port": 8090,
  "rerank_port": 8091
}
```

---

## Test Target Configuration Entity (`tests/conftest.py`)

서버 테스트 실행 시 실행 플랫폼(`10.0.0.x` 대역 등)의 실 IP를 동적으로 주입하는 피스처 엔티티 구조입니다.

### Entity: `TestNetworkTarget`

| Field Name | Type | Resolution Source | Description |
| :--- | :--- | :--- | :--- |
| `target_host_ip` | `string` | `os.environ["HOST_IP"]` → `NetworkDetector.get_active_lan_ips()[0]` | 실행 플랫폼의 유효한 실 네트워크 IP (127.0.0.1 사용 금지) |
| `base_url` | `string` | `f"http://{target_host_ip}:{MAIN_PORT}"` | 테스트 대상 Base HTTP URL |
