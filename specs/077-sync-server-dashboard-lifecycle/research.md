# Technical Research & Design Decisions: `077-sync-server-dashboard-lifecycle`

**Feature Directory**: [`specs/077-sync-server-dashboard-lifecycle`](file:///home/dev/storage/vllm_serv/specs/077-sync-server-dashboard-lifecycle)  
**Spec**: [`spec.md`](spec.md)  

---

## 1. Technical Decisions

### Decision 1: Dual PID File Tracking (`vllm_serv.pid` & `vllm_dashboard.pid`)

- **Decision**: `vllm_serv.pid` (Port 8081 메인 서버 PID)와 `vllm_dashboard.pid` (Port 8082 웹 대시보드 PID)를 이원화하여 개별 보존합니다.
- **Rationale**: 메인 인퍼런스 서버와 Uvicorn 웹 대시보드가 각각 독립된 Python 데몬 프로세스로 가동되므로, 두 프로세스의 PID를 파일 시스템 수준에서 명시적으로 추적 및 관리하기 위함입니다.
- **Alternatives Considered**: 
  - 단일 PID 파일에 두 PID를 공백으로 저장하는 방식 (파싱 복잡성 증가로 기각)
  - PID 파일 없이 `pgrep`만으로 탐색하는 방식 (동일 유저의 타 인스턴스 오탐 위험으로 기각)

### Decision 2: 30초 Readiness 동시 검증 및 원자적 롤백 (Clean Exit)

- **Decision**: `start_server.sh` 실행 시 8081 메인 API 서버(`/health` 또는 `/v1/models`)와 8082 웹 대시보드(`/`)의 HTTP 통신 가능 상태를 30초간 매 초 프로빙합니다. 30초 이내 두 포트가 동시에 준비되지 않을 경우, 두 데몬을 모두 `SIGKILL`로 즉시 강제 종료하고 PID 파일을 삭제한 후 진단 로그(`tail -n 15 logs/server.log`)를 출력하며 종료 코드 1로 리턴합니다.
- **Rationale**: 어느 한쪽 프로세스만 가동된 파편화 상태(Orphan)를 물리적으로 차단하여 GPU VRAM 누수 및 허위 정상 출력을 방지합니다.
- **Alternatives Considered**: 한쪽 포트만 먼저 구동되고 다른 포트는 비동기 로딩 대기 (VRAM 점유 상태에서 서비스 불능으로 기각)

### Decision 3: 3중 다중 프로세스 타겟 종료 및 VRAM 100% 해제 (`stop_server.sh`)

- **Decision**: `stop_server.sh` 실행 시 (1) `vllm_serv.pid` 및 `vllm_dashboard.pid` 파일 수집 PID 종료, (2) `pgrep -f "src.api.server"` 및 `pgrep -f "uvicorn src.api.main:app"` 패턴 탐색 프로세스 종료, (3) 하위 C++ 인퍼런스 데몬 `pgrep -f "llama-server"` 잔여 프로세스 100% 강제 청소를 3단계로 수행합니다. SIGTERM 후 5초 이내 미종료 시 SIGKILL로 전환합니다.
- **Rationale**: PID 파일 누락이나 좀비 프로세스 상주 상황에서도 GPU VRAM 및 네트워크 포트를 100% 원자적으로 회수합니다.
- **Alternatives Considered**: PID 파일 대상만 종료 (대시보드 또는 llama-server 좀비 프로세스가 VRAM을 수00MB~수GB 점유한 채 남는 버그 발생으로 기각)

### Decision 4: 분리된 프로세스 및 포트/DOM 헬스 리포팅 (`status_server.sh`)

- **Decision**: `status_server.sh` 출력 시 8081 메인 서버 프로세스(PID)와 8082 대시보드 프로세스(PID)를 라인별로 분리하여 구동 여부를 표시하고, REST API와 웹 대시보드 HTML DOM 키워드 수신 상태를 정밀 출력합니다.
- **Rationale**: 단독 상주 파편화 상태 발생 시 운영자가 어느 포트/프로세스가 문제인지 시각적으로 즉시 식별할 수 있습니다.

### Decision 5: `setup.sh` 생성 템플릿 정합성 및 `chmod +x` 전역 강제

- **Decision**: `scripts/setup.sh` 내에 포함된 HEREDOC 생성 템플릿을 동일한 동시 원자적 제어 로직으로 갱신하고, 스크립트 작성 완료 시 `chmod +x`를 모든 제어 스크립트에 강제 적용합니다.
- **Rationale**: `setup.sh`를 통한 환경 재구성 시에도 스크립트 간 동작 불일치를 물리적으로 차단합니다.
