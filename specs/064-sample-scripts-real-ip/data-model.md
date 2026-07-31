# Data Model: 샘플 스크립트 실 IP 동적 자동 감지(192.168.0.x / 10.0.0.x / 듀얼 랜포트 지원) 및 연동 설정 개선

**Feature**: `064-sample-scripts-real-ip`

## Entities & Data Schemas

### 1. Dynamic Server Host Resolution Entity (`ServerHostConfig`)
동적 호스트 자동 탐지 및 포트 설정 객체.

- **`detected_lan_ip`**: `str` (예: `"10.0.0.41"` 또는 `"192.168.0.15"`, `NetworkDetector`로 자동 추출)
- **`env_server_host`**: `Optional[str]` (`SERVER_HOST` 환경변수값)
- **`resolved_host`**: `str` (최종 결정된 호스트 주소, 예: `"http://10.0.0.41"`)
- **`llm_endpoint`**: `str` (`"{resolved_host}:8081/v1/chat/completions"`)
- **`embedding_endpoint`**: `str` (`"{resolved_host}:8090/v1/embeddings"`)
- **`rerank_endpoint`**: `str` (`"{resolved_host}:8091/v1/embeddings"`)

---

### 2. Dual LAN Interface Status Entity (`NetworkInterfaceInfo`)
- **`name`**: `str` (인터페이스명, 예: `"eth0"`, `"eth1"`, `"enp3s0"`)
- **`ip_address`**: `Optional[str]` (IPv4 주소)
- **`is_active`**: `bool` (`stat.isup` 여부)
- **`is_usable_lan`**: `bool` (루프백/APIPA 169.254 제외 유효 LAN 여부)
