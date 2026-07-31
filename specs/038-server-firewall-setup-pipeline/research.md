# Phase 0 Research: 서버 방화벽 구축 파이프라인 전수 검토 및 E2E 실측 테스트 (038-server-firewall-setup-pipeline)

## Technical Decisions & Rationale

### 1. TTY 감지 기반 방화벽 포트 개방 승격 및 진단 가이드 아키텍처
- **Decision**: `setup.sh` 및 `start_server.sh` 구동 시 `[ -t 1 ]` (TTY 터미널 대화형) 여부를 감지합니다.
  - TTY 대화형 환경: `sudo ufw allow 8081/tcp` 및 `sudo ufw allow 8089/tcp`를 직접 호출하여 사용자가 `sudo` 비밀번호를 입력해 즉시 포트를 개방하도록 유도.
  - 비대화형(non-TTY / CI) 환경: `sudo -n ufw allow` 시도 후 권한 부족 실패 시 붉은색 강조 박스 로그로 즉시 복구 가능한 수동 실행 명령어(`sudo ufw allow 8081/tcp`) 안내.
- **Rationale**: `sudo -n` 비대화형 명령 실패로 인해 방화벽 포트 등록이 무음 거부되어 대시보드가 차단되는 현상을 근본 방지합니다.

### 2. 루프백(127.0.0.1) 탈피 및 서버 실물 IP 기반 Playwright E2E UI 테스트 도입
- **Decision**: `tests/e2e/test_dashboard_e2e.py`에 서버 물리 LAN IP (`http://10.0.0.41:8081/dashboard/`) 타겟 Playwright E2E 테스트 수트를 신설합니다.
- **Rationale**:
  - 기존 메모리 인메모리 `TestClient` 테스트는 실제 커널 `ufw` 방화벽 차단 여부를 검증하지 못했습니다.
  - 서버 물리 IP를 통해 실제 소켓 핸드셰이크, HTML/CSS/JS 렌더링, 4대 탭 클릭 전환, Playground 프롬프트 스트리밍 및 감사 로그 출력을 100% 실측 검증합니다.

### 3. 헌장 v1.3.1 준수 실측 테스트 검증 규격 (`REAL_NETWORK_TEST=1`)
- **Decision**: 네트워크 및 방화벽 테스트 코드 내 인메모리 목업(In-memory Mock) 사용 0%.
- **Rationale**:
  - `socket.create_connection(("10.0.0.41", 8081), timeout=3.0)` 및 `subprocess.run(["ufw", "status"])` 결과 파싱을 통해 물리 커널 룰셋과 포트 개방 상태를 실측 검증합니다.
