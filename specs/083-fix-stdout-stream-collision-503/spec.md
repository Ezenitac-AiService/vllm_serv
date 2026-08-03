# Feature Specification: stdout 스트림 동시 읽기 충돌 해결 및 채팅 엔드포인트 503 오류 근본 수정

**Feature Short Name**: `fix-stdout-stream-collision-503`  
**Target Directory**: `specs/083-fix-stdout-stream-collision-503/`  
**Status**: DRAFT  
**Date**: 2026-08-03  

---

## 1. 개요 및 목적 (Overview & Goals)

### 1.1 배경 (Background)
이전 스펙(082) 반영 후에도 데몬 구동 후 `/v1/chat/completions` 엔드포인트 호출 시 지속적으로 `503 Service Unavailable` 오류가 발생하는 현상이 관측되었습니다.
원인 분석 결과, `ProcessManager.spawn_process()`가 서브프로세스의 `stdout`에 대해 `_drain_stdout` 비동기 태스크를 생성한 상태에서, `LlamaManager._start_server_subprocess()`가 동일한 `stdout` 스트림에 대해 `_monitor_process` 태스크를 중복으로 생성하여 `proc.stdout.readline()`을 동시에 호출하고 있었습니다.

이로 인해 Python `asyncio` 내부에서 `RuntimeError: read() called while another coroutine is already waiting for incoming data` 예외가 발생하고, 프로세스 모니터링 태스크가 무소음으로 파괴되면서 `ProcessManager.state`가 `ERROR` 또는 `UNLOADED` 상태로 전이되어 역방향 프록시 차단막(503 Guard)이 발동된 것으로 확인되었습니다.

### 1.2 목적 (Goals)
1. **단일 스트림 드레인 표준화**: 서브프로세스의 `stdout` 스트림에 대한 중복 `readline()` 호출을 제거하고, `ProcessManager._drain_stdout`으로 로그 드레인 및 상태 모니터링을 일원화합니다.
2. **503 서비스 거부 근본 해제**: 서빙 프로세스의 READY 상태가 충돌 없이 유지되도록 보장하여 `/v1/chat/completions`, `/health`, `/v1/models` 엔드포인트의 HTTP 200 OK 연속 응답을 복구합니다.
3. **회귀 방지 단위/통합 테스트**: 동일 스트림 중복 대기 방지 검증 테스트 및 대화 생성 E2E 테스트 수트를 구축합니다.

---

## 2. 사용자 시나리오 및 수용 기준 (User Stories & Acceptance Criteria)

### US1: 단일 스트림 모니터링을 통한 엔드포인트 응답 회복 (Priority: P1) 🎯 MVP
**사용자 관점**: 개발자 및 클라이언트는 `./start_server.sh`로 데몬 서버를 실행한 후 `samples/sample_01_chat.py` 및 `diagnose_server_health.py`를 실행했을 때 503 오류 없이 200 OK와 올바른 대화 답변을 받아보아야 한다.

- **AC 1.1**: `ProcessManager`와 `LlamaManager` 간 `stdout.readline()` 경합이 제거되어 `RuntimeError: read() called while another coroutine...` 경고/에러가 발생하지 않아야 한다.
- **AC 1.2**: `uv run scripts/diagnose_server_health.py` 실행 시 `/v1/chat/completions`가 `✅ 200 OK` 및 `STATUS: 🎉 SYSTEM HEALTHY`를 기록해야 한다.
- **AC 1.3**: `uv run samples/sample_01_chat.py` 실행 시 OpenAI 규격 JSON 응답과 생성된 텍스트가 정상 출력되어야 한다.

### US2: 보조 프로세스(Embedding/Reranker) 및 메인 LLM의 독립적 로그 드레인 보장 (Priority: P2)
**사용자 관점**: 보조 서비스(bge-m3, bge-reranker-v2-m3) 및 메인 서빙 모델(qwen3.5-4b) 프로세스가 각각 고유한 포트(8089, 8090, 8091)에서 고유 스트림 드레인 태스크만을 소유해야 한다.

- **AC 2.1**: 포트 8089, 8090, 8091의 서브프로세스가 동시 가동되더라도 스트림 독점 충돌이 발생하지 않아야 한다.
- **AC 2.2**: 백그라운드 구동 후 `./status_server.sh` 조회 시 메인 서버 및 대시보드가 정상 `🟢 구동 중 (RUNNING)` 상태를 유지해야 한다.

---

## 3. 기능 요구사항 (Functional Requirements)

- **FR-001**: `ProcessManager`는 서브프로세스 생성 시 단 하나의 비동기 `_drain_stdout` 태스크만 `proc.stdout`에 할당해야 하며, 외부 클래스가 동일 `StreamReader`에 직렬/병렬로 `readline()`을 직접 호출하지 못하도록 캡슐화해야 한다.
- **FR-002**: `LlamaManager`는 `ProcessManager` 내부의 단일 스트림 드레인 태스크가 파싱한 VRAM 오프로드 상태 및 Readiness 이벤트를 콜백 또는 상태 구독(EventBroadcaster)으로 수신해야 한다.
- **FR-003**: `ProcessManager._drain_stdout`은 log print, VRAM offload log parsing, Readiness detection, process exit waiting(proc.wait)을 일체형(All-in-one)으로 처리하여 예외 발생 시 프로세스 상태를 정확히 `ERROR` 또는 `READY`로 전이시켜야 한다.
- **FR-004**: `diagnose_server_health.py` 및 `sample_01_chat.py` 호출 시 503 게이트웨이 타임아웃이 발생하지 않도록 헬스 상태 반환 로직을 동기화해야 한다.

---

## 4. 성과 및 성공 기준 (Success Criteria)

- **SC-001**: `uv run scripts/diagnose_server_health.py` 통과 (모든 포트/엔드포인트 `✅ 200 OK`).
- **SC-002**: `uv run samples/sample_01_chat.py` 호출 100% 성공 (`✅ [응답 성공]`).
- **SC-003**: `logs/server.log` 상에 `RuntimeError: read() called while another coroutine is already waiting for incoming data` 로그 0건 달성.

---

## 5. 가정 및 제약사항 (Assumptions & Constraints)

- **헌법 I조 (한국어 문서화)**: 모든 문서 및 사용자 보고는 한국어로 작성한다.
- **헌법 II조 (Zero Mock)**: 실제 서브프로세스와 하드웨어 GPU VRAM 및 네트워크 포트(8081, 8089, 8090, 8091) 상에서 실측 검증한다.
