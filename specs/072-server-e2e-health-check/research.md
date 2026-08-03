# Research: LLM 서버 서비스 모델, API 엔드포인트, E2E 대시보드, 방화벽 및 LAN 접속 통합 진단 (072-server-e2e-health-check)

## Research Topic 1: 동적 LAN IP 감지 및 방화벽/포트 바인딩 진단 패턴

### Decision
`src/core/network_detector.py`의 `NetworkDetector` 모듈을 활용하여 서버의 유효 LAN IP(`10.0.0.x` 또는 `192.168.0.x`)를 동적 감지하고, 해당 IP 및 포트(8081 LLM 메인, 8082 대시보드)에 대해 소켓 바인딩 및 접속 가능 상태를 진단.

### Rationale
- `127.0.0.1` / `localhost`는 동일 루프백 인터페이스에 한정되어 다른 내부 네트워크망 기기에서 통신 가능한지 검증하지 못함.
- `NetworkDetector.get_active_lan_ips()`를 통해 실제 활성 NIC IP를 감지하고, 소켓 연결 시도(`socket.create_connection`)를 통해 방화벽 포트 차단 여부를 정확히 점검 가능.

---

## Research Topic 2: 웹 대시보드 UI 브라우저 E2E 검증 기법

### Decision
Playwright 브라우저 테스트 및 `httpx` 비동기 웹 응답 진단을 결합하여 웹 대시보드(8082 포트) 메인 UI 및 렌더링 상태를 자동 검증.

### Rationale
- 단순 HTTP GET 요청만으로는 JavaScript 대시보드 프론트엔드의 실제 브라우저 렌더링 여부를 검증하기 부족함.
- Playwright 헤드리스 브라우저 테스트 수트를 추가하여 실제 DOM 요소 렌더링 및 404/500 에러 부재를 확실하게 검증 가능.

---

## Research Topic 3: LLM 서빙 모델 목록 및 API 엔드포인트 검증

### Decision
OpenAI 호환 `/v1/models` API를 호출하여 활성 서빙 모델 목록(`qwen3.5-4b` 등)을 추출하고, `/v1/chat/completions` 및 `/health` 엔드포인트에 헬스체크 핑을 전송하여 통합 진단 리포트를 생성.
