# Technical Research: Codebase Efficiency Refactoring

**Feature**: `006-codebase-efficiency-refactoring`  
**Date**: 2026-07-29

## Executive Summary

본 연구 문서는 `vllm_serv` 프로젝트의 리팩토링 목표(모듈화 책임 분리, 원자적 I/O 안정성, 비동기 커넥션 풀 및 스트림 관리)를 달성하기 위한 4대 핵심 기술 결정 사항과 설계 이론적 근거를 명시합니다.

---

## Technical Decisions & Rationale

### 1. ProcessManager & EventBroadcaster 책임 분리 (SRP)
- **Decision**: `LlamaManager` 내에 병합되어 있던 서브프로세스(`llama-server`) 수명주기 제어 및 SSE 이벤트 구독 브로드캐스트 로직을 `ProcessManager`와 `EventBroadcaster`로 분리한다.
- **Rationale**:
  - `ProcessManager`: 서브프로세스 런치, `poll()`, 킬 타임아웃 에스컬레이션(`SIGTERM` ➔ `SIGKILL`), VRAM 릴리스 감지만 전담.
  - `EventBroadcaster`: 구독자 관리(add/remove listener), `asyncio.Queue` 기반 SSE 브로드캐스트 및 15초 하트비트 주입 전담.
  - `EventBroadcaster` 비동기 큐에 Bounded Queue(`maxsize=100`)를 적용하여 느린 전송 구독자로 인한 메모리 백프레셔(Backpressure) 현상을 원천 방지함.
- **Alternatives Considered**:
  - 기존 클래스 내부 메소드 분리: 클래스가 여전히 비대해지고 단위 테스트 시 서브프로세스 mock이 까다로움. (기각)

---

### 2. 동일 디렉토리 원자적 I/O (Atomic Replace with Same-Dir Temp File)
- **Decision**: `ConfigManager` 설정 저장 시 `tempfile.NamedTemporaryFile(dir=os.path.dirname(config_path))`로 동일 디렉토리 내 임시 파일을 생성 후 `os.replace` 수행.
- **Rationale**:
  - `os.replace`는 POSIX `rename(2)` 시스템 콜을 호출하여 동일한 디바이스 마운트 지점(`st_dev`) 상에서 원자적(Atomic)으로 파일을 스왑함.
  - 시스템 임시 디렉토리(`/tmp` - tmpfs/ramdisk)를 사용할 경우, 프로젝트 파일시스템과의 경계를 넘어 교차 디바이스 오류(`Errno 18 EXDEV: Invalid cross-device link`)가 발생하여 원자적 쓰기가 깨질 위험이 존재함.
- **Alternatives Considered**:
  - 단순 `open(path, "w")`: 쓰기 중간 OS 셧다운 시 파일 0바이트 손상 위험. (기각)
  - `shutil.move`: 원자적 연산을 보장하지 않고 copy+unlink로 fallback되어 오염 위험 존재. (기각)

---

### 3. FastAPI Lifespan 커넥션 풀링 (`httpx.AsyncClient`)
- **Decision**: FastAPI `@asynccontextmanager` 기반 `lifespan` 내에서 `httpx.AsyncClient`를 초기화하여 `app.state.http_client`로 등록하고, 종료 시 `await client.aclose()`를 실행.
- **Rationale**:
  - 매 요청마다 `httpx.AsyncClient()`를 생성/파기하면 TCP 3-way handshake 및 소켓 TIME_WAIT 포화가 발생함.
  - `httpx.Limits(max_keepalive_connections=20, max_connections=100)`를 설정하여 커넥션 풀을 효율적으로 재사용하고 리소스 누수를 차단함.
- **Alternatives Considered**:
  - 글로벌 모듈 변수 싱글톤: FastAPI 앱 수명주기와 분리되어 테스트 isolation 및 graceful shutdown 시 소켓 누수 위험. (기각)

---

### 4. 클라이언트 접속 이탈 감지 및 프록시 스트림 캔슬레이션
- **Decision**: `inference_api.py` 역방향 프록시 스트리밍 제너레이터 루프 내에서 `await request.is_disconnected()`를 체크하여 조기 종료 시 업스트림 스트림을 바로 닫음.
- **Rationale**:
  - 클라이언트가 HTTP 스트리밍 도중 이탈(Tab close, Network Drop)했을 때 하위 `llama-server`로의 백엔드 스트림을 끊지 않으면 GPU/CPU 추론 자원이 지연 소모됨.
- **Alternatives Considered**:
  - 타임아웃 기반 간과: 클라이언트가 끊어져도 전체 응답 생성이 완료될 때까지 프로세스가 차단됨. (기각)
