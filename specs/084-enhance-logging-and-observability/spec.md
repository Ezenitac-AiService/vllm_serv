# Feature Specification: 서버 진단 로그 강화 및 포트 점유(Errno 98) 정밀 추적 고도화

**Feature Short Name**: `enhance-logging-and-observability`  
**Target Directory**: `specs/084-enhance-logging-and-observability/`  
**Status**: DRAFT  
**Date**: 2026-08-03  

---

## 1. 개요 및 원인 분석 리포트 (Overview & Empirical Root Cause Report)

### 1.1 실측 로그 기반 원인 분석 (Empirical Diagnosis from `/logs`)
`/home/dev/storage/vllm_serv/logs` 디렉토리의 실제 로그 파일 분석 결과:

1. **`logs/error.log` 정보 부족 문제**:
   - `error.log`에는 단순 HTTP 응답 상태 메시지(`[10.0.0.41] /v1/chat/completions 503 [HTTP_503]: Response status 503`)만 단편적으로 기록되고 있었습니다.
   - 503 오류를 유발한 **내부 예외 클래스, 스택 트레이스(Traceback), 바인딩 포트 정보, 원인 메시지**가 전혀 기록되지 않아 원인 파악이 추측에 의존하게 되었습니다.

2. **`logs/server.log` 무한 크래시 루프 원인**:
   - `server.log` 확인 결과, `AuxiliaryManager`가 보조 인스턴스(bge-m3, bge-reranker-v2-m3)를 5초 주기로 무한히 재시도(`AuxiliaryManager FR-007: Embedding process crash detected!`)하고 있었습니다.
   - 서브프로세스 파이썬 모듈(`python -m llama_cpp.server`)을 직접 실행하여 확인한 결과, 근본 원인은 **`ERROR: [Errno 98] error while attempting to bind on address ('0.0.0.0', 8090): address already in use`**였습니다.
   - 이전 실행에서 남아있던 잔존/좀비 프로세스가 포트 8090/8091을 점유하고 있어 서브프로세스가 즉시 종료코드 3으로 크래시되었고, 이로 인해 `ProcessManager` 상태가 불안정해져 역방향 프록시가 503을 반환했습니다.

### 1.2 고도화 목적 (Goals)
1. **상세 오류 로그 자율 기록 (Detailed Traceback Logging)**: 503/500 등 예외 발생 시 `logs/error.log`에 원인 예외, 발생 포트, 스택 트레이스, 세부 메시지를 투명하게 기록합니다.
2. **포트 바인딩 충돌(`[Errno 98]`) 자동 정리**: `ProcessManager`가 프로세스 개설 전 타겟 포트(8089, 8090, 8091) 점유 프로세스를 완전히 정리하여 포트 충돌을 사전에 차단합니다.
3. **서브프로세스 캡처 로그 원자적 출력**: 서브프로세스의 `stderr` 및 비정상 종료 코드를 즉시 감지하여 `server.log` 및 `error.log`에 원인을 명시합니다.

---

## 2. 사용자 시나리오 및 수용 기준 (User Stories & Acceptance Criteria)

### US1: 실측 로그 기반 정밀 에러 트레이싱 (Priority: P1) 🎯 MVP
**사용자 관점**: 서버 운영자 및 개발자는 503 Service Unavailable 오류가 일어났을 때 `logs/error.log`만 확인하더라도 정확한 예외 원인과 스택 트레이스를 파악할 수 있어야 한다.

- **AC 1.1**: `/v1/chat/completions` 등 역방향 프록시에서 503 오류가 발생할 때, `logs/error.log`에 요청 ID, 타겟 포트, 발생 사유(`detail`), Python 예외 스택 트레이스가 구체적으로 기록되어야 한다.
- **AC 1.2**: 서브프로세스가 non-zero exit code(예: exit code 3)로 종료될 경우, 서브프로세스가 출력한 마지막 `stderr` 문맥이 `logs/error.log`에 명시되어야 한다.

### US2: 포트 8089/8090/8091 강제 정돈 및 바인딩 보장 (Priority: P1)
**사용자 관점**: 서버 구동 시 기존 잔존 프로세스로 인한 `Errno 98 address already in use` 오류가 발생하지 않고 Clean 바인딩이 이루어져야 한다.

- **AC 2.1**: `ProcessManager.spawn_process()` 실행 전 타겟 포트(8089, 8090, 8091)를 점유 중인 잔존 PID를 강제 정돈(SIGKILL)하고 포트 해제를 확인한 후 프로세스를 개설해야 한다.
- **AC 2.2**: `AuxiliaryManager`가 보조 모델 로드 실패 시 무한 크래시 루프에 빠지지 않고, 서킷 브레이커 조치 후 이유를 `error.log`에 정직하게 기록해야 한다.

---

## 3. 기능 요구사항 (Functional Requirements)

- **FR-001**: `src/api/middleware/client_access_logger.py` 및 `src/api/routes/inference_api.py`에 상세 예외 핸들러를 추가하여, HTTP 5xx/4xx 응답 시 `traceback.format_exc()` 및 HTTP `detail` 메시지를 `logs/error.log` 파일에 타임스탬프와 함께 로깅한다.
- **FR-002**: `ProcessManager.spawn_process()`에 포트 정돈 로직을 강화하여, `0.0.0.0:PORT` 또는 `127.0.0.1:PORT`를 소켓 점유 중인 프로세스를 선제적으로 탐지 및 정리하고 `[Errno 98]` 바인딩 에러를 예방한다.
- **FR-003**: `ProcessManager._drain_stdout()` 및 비동기 프로세스 모니터링 시 서브프로세스 비정상 종료를 탐지하면 `proc.returncode`와 마지막 5줄의 `stderr`/`stdout` 출력 내용을 `logs/error.log`에 기록한다.
- **FR-004**: `diagnose_server_health.py` 검증 시 `/v1/chat/completions` 호출 실패가 발생하면 503 반환 사유(예: "backend process status = ERROR, detail = Errno 98")를 터미널 리포트에 투명하게 노출한다.
- **FR-005**: `scripts/stop_server.sh` 종료 스크립트를 고도화하여 `pgrep -f "llama-server"` 외에도 `pgrep -f "llama_cpp.server"` 및 8081, 8082, 8089, 8090, 8091 포트 소켓을 바인딩하는 모든 잔존 프로세스를 완전 정리하도록 보장한다.


---

## 4. 성공 기준 (Success Criteria)

- **SC-001**: `logs/error.log` 파일에 단일 줄 요약(`Response status 503`) 외에 예외 메시지 및 상세 원인이 포함된 다중 행 로그가 기록됨.
- **SC-002**: `./start_server.sh` 구동 시 `logs/server.log` 상에 `Errno 98 address already in use` 에러가 0건 발생함.
- **SC-003**: `uv run scripts/diagnose_server_health.py` 및 `uv run samples/sample_01_chat.py` 100% 성공 (`STATUS: 🎉 SYSTEM HEALTHY`).

---

## 5. 프로젝트 헌법 준수사항 (Constitution Discipline)

- **헌법 I조 (한국어 문서화)**: 명세서 및 품질 보고서는 한국어로 작성.
- **헌법 II조 (Zero Mock)**: 가짜 성공 및 불투명 예외 숨김을 전면 금지하고 실제 로그 파일 및 프로세스 상태를 실측 연동함.
