# Research: samples 예제 스크립트의 서비스 플랫폼 IP 대역 접속 보장 및 테스트 스크립트 실 IP 검증 분리 (070-samples-platform-ip-separation)

## Research Topic 1: samples/ 전용 외부 의존성 없는 독립 설정 파일 로더 (config.json & .env)

### Decision
`samples/common.py`에 표준 Python 라이브러리(`os`, `json`, `pathlib`)만을 사용하는 `get_server_host()` 호스트 감지기 구현.

### Rationale
- `samples/`의 코드는 외부 사용자 및 훈련생들이 가벼운 클라이언트 환경에서 복사하여 재활용하는 예제 스크립트입니다.
- 추가 3rd-party 패키지(`python-dotenv` 등)에 대한 의존성을 배제하고 표준 라이브러리만을 활용해 `samples/config.json`, `samples/.env` 및 `SERVER_HOST` 환경변수를 순서대로 탐색하여 서버 URL을 로드합니다.
- 우선순위 계층 구조:
  1. `SERVER_HOST` / `OPENAI_BASE_URL` / `VLLM_API_BASE` (시스템/셸 환경변수 최우선)
  2. `samples/.env` 파일 내 `SERVER_HOST` 선언
  3. `samples/config.json` 내 `"server_host"` 또는 `"api_url"` 설정
  4. 기본 서비스 플랫폼 IP (`http://192.168.0.100`)

### Alternatives Considered
- `python-dotenv` / `pydantic-settings` 활용: 클라이언트 환경에 불필요한 패키지 설치 요구가 발생하므로 제외.
- 서버 내부 `src.core.network_detector` 임포트 사용: 클라이언트 예제와 백엔드 패키지 간의 결합도가 발생하므로 제외.

---

## Research Topic 2: tests/ 수트의 127.0.0.1/localhost 금지 및 동적 실 IP 감지 피스처

### Decision
`tests/conftest.py` 내 `target_host_ip` 세션 피스처에서 `NetworkDetector.get_active_lan_ips()`를 활용해 현 실행 플랫폼(`10.0.0.x` 등)의 실제 LAN IP를 동적으로 주입하고, `127.0.0.1` 및 `localhost` 루프백 지정을 차단.

### Rationale
- 테스트 서버 가동 시 127.0.0.1 루프백 주소로만 수신 확인을 할 경우, 실제 내부 네트워크 인터페이스(`10.0.0.x` 또는 `192.168.0.x`)를 통한 수신이 방화벽이나 바인딩 오류로 차단된 상태를 감지하지 못합니다.
- `NetworkDetector`를 통해 실제 네트워크 카드의 유효 IP를 자동으로 탐지하여 테스트 타겟으로 설정함으로써 실 네트워크 접속 가능 여부를 100% 검증합니다.

### Alternatives Considered
- 하드코딩된 IP(`10.0.0.41`) 사용: 테스트가 가동되는 개별 환경(다른 IP 대역)에서 회귀 실패가 발생할 수 있으므로 동적 탐지가 우수함.
