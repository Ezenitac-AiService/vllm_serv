# Research: 서버 진단 로그 강화 및 포트 점유(Errno 98) 정밀 추적

## 1. 503 오류 발생 시 상세 예외 및 스택 트레이스 로깅 (FR-001)

### Decision
`src/api/middleware/client_access_logger.py` 및 `src/api/routes/inference_api.py`에서 5xx/4xx HTTP 예외가 포착되면 `traceback.format_exc()`와 HTTP `detail` 메시지를 `logs/error.log`에 다중 행(Multi-line) 타임스탬프와 함께 기록한다.

### Rationale
기존 `client_logger.py`는 단 1줄의 상태 메시지(`Response status 503`)만 기록하여 구체적 원인(예: PortCollision, ConnectTimeout, ValueError 등)을 파악할 수 없었다. Python `traceback` 모듈을 연동하면 예외 발생 위치와 원인을 로그 파일에서 100% 추적 가능하다.

---

## 2. 포트 8081, 8082, 8089, 8090, 8091 좀비 프로세스 선제 정돈 (FR-002, FR-005)

### Decision
1. `ProcessManager.spawn_process()`가 서브프로세스를 개설하기 직전, `_cleanup_zombie_on_port(port)` 메소드를 호출하여 `0.0.0.0:port` 또는 `127.0.0.1:port`에 남아 있는 기존 잔존 PID를 `fuser -k -9 {port}/tcp` 및 `lsof -t -i:{port}`로 선제 SIGKILL 강제 종료한다.
2. `scripts/stop_server.sh` 스크립트에 `pgrep -f "llama_cpp.server"` 탐지 및 8081, 8082, 8089, 8090, 8091 포트 바인딩 프로세스 강제 정리 명령어를 추가한다.

### Rationale
`stop_server.sh`가 `llama-server` C++ 바이너리만 탐지하고 `python -m llama_cpp.server` 프로세스를 놓쳐서 포트 8090/8091 소켓이 `TIME_WAIT` 또는 고아(Orphan) 상태로 남아 `[Errno 98] address already in use`가 발생했다. 포트 레벨 소켓 정리 및 `llama_cpp.server` 프로세스 정리를 결합하여 100% 재발을 방지한다.

---

## 3. 서브프로세스 non-zero exit code 시 stderr 맥락 캡처 (FR-003)

### Decision
`ProcessManager._drain_stdout` 비동기 루프에서 서브프로세스의 최근 10개 출력 행을 링 버퍼(Ring Buffer)로 유지하며, 프로세스가 exit code != 0으로 비정상 종료 시 마지막 stderr/stdout 로그 5줄을 `logs/error.log` 및 `logs/server.log`에 즉시 명시적 에러 블록으로 출력한다.

### Rationale
서브프로세스가 튕겼을 때 파이썬 코드가 무소음으로 종료 상태만 읽어서 상태를 전환하던 문제를 해결하고, 에러 로그 파일만으로 서브프로세스의 종료 원인을 직관적으로 파악할 수 있게 된다.
