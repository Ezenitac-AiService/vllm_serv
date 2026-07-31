# Research: 샘플 스크립트 실 IP 동적 자동 감지(192.168.0.x / 10.0.0.x / 듀얼 랜포트 지원) 및 연동 설정 개선

**Feature**: `064-sample-scripts-real-ip`

## Technical Decisions & Rationale

### Decision 1: 실 IP 동적 자동 감지 및 듀얼 랜포트 필터링 아키텍처
- **선택된 방식**: `samples/common.py` 내 `get_server_host()` 구현 시 `src.core.network_detector.NetworkDetector.get_active_lan_ips()` 파이프라인 결합
- **이유**: `NetworkDetector`는 `psutil.net_if_stats()`와 `psutil.net_if_addrs()`를 사용하여 물리 인터페이스 활성화 상태(`stat.isup == True`)를 직접 조회합니다. 듀얼 랜포트 서버에서 1개 포트가 케이블 미연결/다운 상태이거나 미할당(`169.254.x.x`) 상태일 때 이를 엄격히 필터링하고 실제 3종 플랫폼(`192.168.0.x` 또는 `10.0.0.x`)의 사용 가능한 유효 LAN IPv4 주소를 동적 반환합니다.
- **대안 검토**: `socket.gethostbyname(socket.gethostname())` 단순 호출 — 듀얼 랜포트 환경에서 미할당/비활성 포트 IP나 `127.0.1.1`을 잘못 반환할 가능성이 높아 기각함.

### Decision 2: 우선순위 기반 호스트 설정 제어 (Environment Variable Override)
- **선택된 방식**: 1순위: `SERVER_HOST` / `OPENAI_BASE_URL` / `VLLM_API_BASE` 환경변수 ➡️ 2순위: `NetworkDetector.get_active_lan_ips()` 동적 감지 첫 번째 유효 LAN IP ➡️ 3순위: `127.0.0.1` 오프라인 폴백
- **이유**: 개발자 수동 오버라이드 및 CI/CD 오프라인 루프백 테스트 환경과의 호환성을 100% 보장하면서 하드코딩 없는 유연한 설정을 완성함.

### Decision 3: 샘플 스크립트 전면 바인딩 개정 (`sample_01` ~ `sample_05`)
- **선택된 방식**: `samples/sample_01_chat.py` ~ `samples/sample_05_structured_output.py` 모듈 상단의 `SERVER_HOST = "http://127.0.0.1"` 하드코딩을 제거하고 `SERVER_HOST = get_server_host()` 동적 함수 호출로 대체함.
- **이유**: 샘플 코드를 복사/실행하는 사용자가 192.168.0.x 또는 10.0.0.x 등 어떠한 타겟 플랫폼에서도 코드 수정 없이 즉시 실 IP 서버 엔드포인트(8081, 8090, 8091)로 호출 가능함.
