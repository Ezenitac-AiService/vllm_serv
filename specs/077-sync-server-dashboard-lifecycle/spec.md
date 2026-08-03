# Feature Specification: 메인 서버-대시보드 프로세스 생명주기 원자적 동기화 (`077-sync-server-dashboard-lifecycle`)

**Feature Directory**: [`specs/077-sync-server-dashboard-lifecycle`](file:///home/dev/storage/vllm_serv/specs/077-sync-server-dashboard-lifecycle)  
**Created**: 2026-08-03  
**Status**: In Review (Clarified)  

---

## 1. Overview & Business Value

`vllm_serv` 시스템 구동/종료 제어 스크립트(`start_server.sh`, `stop_server.sh`, `status_server.sh`)의 실행 생명주기를 완벽히 동기화하여, 8081 메인 API 서버와 8082 웹 대시보드 서버 프로세스가 독립적으로 고립(Orphan)되거나 잔여 프로세스로 인해 GPU VRAM이 점유·지연되는 문제를 근본적으로 해결합니다.

`start_server.sh` 및 `stop_server.sh` 실행 시 메인 서버와 대시보드 프로세스를 원자적으로 함께 시작하고 함께 종료하는 메커니즘을 보장합니다.

---

## 2. User Personas & Scenarios

- **Persona**: SRE 운영자 / 시스템 엔지니어 / AI 개발자
- **Scenario**:
  1. 사용자가 `./start_server.sh`를 실행하면 8081 메인 인퍼런스 서버와 8082 웹 대시보드가 원스톱으로 동시에 시작됩니다.
  2. 사용자가 `./status_server.sh`를 실행하면 8081 메인 서버와 8082 대시보드의 구동 상태, PID, 포트 개방 여부, GPU VRAM 점유 현황이 일관되게 출력됩니다.
  3. 사용자가 `./stop_server.sh`를 실행하면 8081 메인 서버, 8082 대시보드 및 잔여 `llama-server` 하위 프로세스가 모두 원자적으로 강제 종료되어 GPU VRAM 및 소켓 포트가 100% 해제됩니다.

---

### User Story 1 - 원자적 동시 서버-대시보드 가동 (`start_server.sh`) (Priority: P1)

사용자가 `./start_server.sh`를 실행할 때 메인 API 서버(8081)와 웹 대시보드(8082)가 결합하여 원스톱으로 가동되고, 어느 하나라도 구동 실패 시 둘 다 완전히 취소(Rollback)되어 파편화된 프로세스가 남지 않아야 합니다.

**Why this priority**: 프로세스 파편화 방지 및 운영 일관성을 확보하는 최우선 과제입니다.

**Independent Test**: `./start_server.sh` 1회 실행 후 8081과 8082 포트 및 PID가 모두 상주하거나, 구동 실패 시 모두 종료되는지 확인합니다.

**Acceptance Scenarios**:

1. **Given** 8081 포트와 8082 포트 프로세스가 모두 중지된 상태에서, **When** `./start_server.sh`를 실행하면, **Then** 8081 API 서버와 8082 uvicorn 대시보드가 동시에 백그라운드로 가동되고 각각 PID 파일(`vllm_serv.pid`, `vllm_dashboard.pid`)에 기록됩니다.
2. **Given** 8081 또는 8082 프로세스 중 어느 하나라도 이미 실행 중인 단독 상주 상태에서, **When** `./start_server.sh`를 실행하면, **Then** 실행을 중단하고 상주 중인 PID 정보를 경고로 출력하며 `./stop_server.sh` 실행 후 재시도하도록 안내합니다.
3. **Given** 구동 대기 중 어느 한 포트라도 Readiness 타임아웃(30초)에 도달하면, **When** 원자적 롤백이 동작하여, **Then** 생성된 8081 메인 프로세스와 8082 대시보드 프로세스를 모두 `SIGKILL`로 정리하고 종료 코드 1로 리턴합니다.

---

### User Story 2 - 원자적 동시 서버-대시보드 완전 종료 (`stop_server.sh`) (Priority: P1)

사용자가 `./stop_server.sh`를 실행할 때 메인 API 서버(8081), 웹 대시보드(8082), 및 C++ `llama-server` 하위 프로세스가 단 하나도 남지 않고 모두 동시 종료되어 VRAM 및 소켓 자원이 완전 해제되어야 합니다.

**Why this priority**: 잔여 프로세스로 인한 GPU VRAM 점유 및 포트 바인딩 충돌을 방지하기 위함입니다.

**Independent Test**: 대시보드만 구동 중이거나 메인 서버만 구동 중인 파편화 상태에서 `./stop_server.sh` 실행 시 `pgrep -f "src.api.server"`, `pgrep -f "uvicorn src.api.main:app"`, `pgrep -f "llama-server"` 결과가 모두 빈 값이 되는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** 8081 메인 서버와 8082 대시보드가 구동 중인 상태에서, **When** `./stop_server.sh`를 실행하면, **Then** 두 프로세스가 모두 SIGTERM(실패 시 SIGKILL)으로 정상 종료되고 관련 PID 파일(`vllm_serv.pid`, `vllm_dashboard.pid`)이 모두 삭제됩니다.
2. **Given** 메인 서버는 중지되었으나 8082 대시보드 프로세스만 좀비 상태로 잔존한 경우, **When** `./stop_server.sh`를 실행하면, **Then** PID 파일 부재 시에도 `pgrep` 프로세스 패턴 탐색을 통해 8082 대시보드 및 llama-server 프로세스까지 감지하여 깨끗하게 제거합니다.
3. **Given** 종료 완료 후, **When** `nvidia-smi` 자원 조회를 수행하면, **Then** 서버 프로세스에 의해 점유되어 있던 VRAM이 완전히 해제된 상태를 리포트합니다.

---

### User Story 3 - 정확한 포트/프로세스 동기화 상태 진단 (`status_server.sh`) (Priority: P2)

사용자가 `./status_server.sh`를 실행할 때 8081 메인 서버와 8082 대시보드의 실제 프로세스 생존 상태, PID 파일 정합성, HTTP REST/DOM 헬스 상태를 명확하게 구분하여 출력해야 합니다.

**Why this priority**: 프로세스 파편화 현상을 즉시 인지하고 운영을 정상화하기 위한 필수 리포팅 기능입니다.

**Independent Test**: `./status_server.sh` 실행 시 8081 프로세스 상태와 8082 대시보드 프로세스 상태가 각각 독립 라인으로 정확하게 표시되는지 검증합니다.

**Acceptance Scenarios**:

1. **Given** 서버 및 대시보드가 구동 중일 때, **When** `./status_server.sh`를 실행하면, **Then** `8081 메인 서버 프로세스: 🟢 구동 중 (PID: ...)` 및 `8082 대시보드 프로세스: 🟢 구동 중 (PID: ...)`로 명확히 분리 리포트됩니다.
2. **Given** 어느 한쪽만 비정상 상주하는 경우, **When** `./status_server.sh`를 실행하면, **Then** 구동 중인 항목과 중지된 항목을 각각 명확히 시각화하여 파편화 상태를 사용자가 즉시 파악할 수 있도록 합니다.

---

### Edge Cases

- **PID 파일과 실제 프로세스 불일치**: `vllm_serv.pid` 또는 `vllm_dashboard.pid`에 기록된 PID의 프로세스가 이미 종료되었더라도 `pgrep -f` 패턴 매칭으로 잔여 좀비 프로세스를 찾아 제거함.
- **`stop_server.sh` 무한 대기 차단**: SIGTERM 후 5초 이내 미종료 시 강제 SIGKILL 전환.
- **`setup.sh` 재실행 시 템플릿 정합성**: `setup.sh` 실행으로 생성되는 `scripts/start_server.sh`, `scripts/stop_server.sh`, `scripts/status_server.sh` 스크립트 템플릿이 동일한 동기화 원자적 제어 로직을 포함해야 함.

---

## 3. Definition of Done (작업 종료 조건) *(mandatory)*

- **DoD-001**: `./start_server.sh` 1회 실행 시 8081 및 8082 두 프로세스가 원자적으로 동시 백그라운드 가동되고 PID 파일 2개가 생성되어야 함.
- **DoD-002**: `./stop_server.sh` 1회 실행 시 8081 API 서버, 8082 uvicorn 대시보드, `llama-server` 잔여 프로세스가 100% 종료되고 PID 파일 및 VRAM 점유가 깨끗이 정리되어야 함.
- **DoD-003**: `./status_server.sh` 실행 시 8081 및 8082 두 서비스의 프로세스 생존 유무와 헬스 상태가 분리되어 정확히 리포트되어야 함.
- **DoD-004**: 통합 및 단단 단위 테스트 통과 (`uv run pytest tests/integration/test_dual_port_readiness.py tests/unit/test_shell_scripts.py`).

---

## 4. Requirements *(mandatory)*

### Functional Requirements

- **FR-001 (동시 원자적 프로세스 가동)**: `start_server.sh`는 8081 메인 서버와 8082 uvicorn 대시보드를 동시 가동하고 `vllm_serv.pid` 및 `vllm_dashboard.pid` 파일에 PID를 각각 기록하며, 한쪽이라도 구동 중인 단독 상주 상태 시 실행 중단 후 `./stop_server.sh` 실행을 안내해야 한다.
- **FR-002 (원자적 시작 실패 롤백)**: `start_server.sh`는 8081 및 8082 중 어느 하나라도 30초 이내 Readiness 상태에 도달하지 못하면 두 프로세스를 모두 원자적으로 SIGKILL 종료(Clean Exit)하고 PID 파일을 제거해야 한다.
- **FR-003 (동시 원자적 프로세스 종료)**: `stop_server.sh`는 `vllm_serv.pid`와 `vllm_dashboard.pid`를 읽어 해당 프로세스를 종료하고, PID 파일 부재 시에도 `src.api.server`, `uvicorn src.api.main:app`, `llama-server` 프로세스를 순회 감지하여 완전 종료해야 한다.
- **FR-004 (분리된 동기화 상태 리포팅)**: `status_server.sh`는 8081 메인 서버와 8082 대시보드 프로세스의 생존 상태(PID), 포트 LISTEN, HTTP/HTML 헬스를 각각 명확히 분리하여 시각화해야 한다.
- **FR-005 (setup.sh 템플릿 완결성)**: `scripts/setup.sh` 내에 수록된 스크립트 생성 HEREDOC 템플릿은 변경된 동시 원자적 구동/종료 로직과 100% 동일한 내용을 포함하고 전역 `chmod +x`를 강제해야 한다.

---

## 5. Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `./stop_server.sh` 실행 후 `pgrep -f "src.api.server"`, `pgrep -f "uvicorn"`, `pgrep -f "llama-server"` 탐색 결과 0건 달성 (잔여 좀비 프로세스 0%).
- **SC-002**: `./start_server.sh` 1회 실행으로 8081 및 8082 두 포트가 모두 정상 LISTEN 상태로 수렴.
- **SC-003**: `status_server.sh` 실행 시 메인 서버 및 대시보드의 상태 오탐 없는 정확한 구분 리포트 달성.

---

## 6. Assumptions

- 표준 설치 환경에서 메인 API 서버 포트는 8081, 웹 대시보드 포트는 8082를 기본으로 사용합니다.
- 프로세스 관리는 Linux `pgrep`, `ps`, `kill` 표준 유틸리티 및 `uv run` 환경을 기준으로 합니다.

---

## 7. Clarifications

### Session 2026-08-03
- **Q**: 8081 또는 8082 단독 상주 상태에서 `start_server.sh` 실행 시 동작 방식 → **A**: Option A (상주 PID 정보를 경고로 출력하고 구동을 중단하며 `./stop_server.sh` 실행 후 재시도하도록 안내)
