# Phase 0 Research: Codebase Refactoring & Architecture Optimization

**Feature Branch**: `specs/017-codebase-refactoring-cleanup`  
**Date**: 2026-07-29

---

## 1. Research Overview & Objectives

본 리서치는 `vllm_serv` 파이썬 소스 코드 전반의 하드코딩 제거, Pydantic v2 기반 강타입 설정 레지스트리 구축, `192.168.0.0/24` 사설 내부망 CIDR 접근제어 미들웨어, 비동기 HTTP 커넥션 풀 싱글톤화, 및 Asyncio Subprocess 안전 해제 패턴을 위한 기술적 연구 결과를 수록합니다.

---

## 2. Technical Decisions & Research Findings

### R-001: Pydantic v2 BaseSettings & Config Registry Pattern
- **Decision**: `ConfigManager` 내부를 Pydantic v2 `BaseSettings` 및 `BaseModel` 기반으로 전환하여 `config/server_config.json`, `config/model_catalog.json` 및 `LLAMA_*` 환경변수를 타입 안전하게 로드합니다.
- **Rationale**:
  - 기존 파이썬 raw `dict` 기반 구조는 존재하지 않는 키 참조 시 `KeyError` 또는 파싱 누락 위험이 존재함.
  - Pydantic v2는 Rust 기반 `pydantic-core` 엔진을 사용하여 파싱 속도가 압도적이며, 환경변수 오버라이딩과 JSON 파싱 우선순위(Precedence)를 선언적으로 보장함.
- **Alternatives Considered**:
  - Standard `json.load()` + TypedDict: 타입 런타임 검증 미지원으로 수동 `isinstance` 체크 코드가 복잡해짐 (기각).

### R-002: FastAPI IP CIDR Network Access Control Middleware Pattern
- **Decision**: `ipaddress` 파이썬 표준 라이브러리의 `ip_network` 및 `ip_address` 모듈을 연동하는 FastAPI 미들웨어를 구현하여 `127.0.0.1` 및 `192.168.0.0/24` CIDR 대역 외 접근 시 `HTTP 403 Forbidden`을 즉시 차단합니다.
- **Rationale**:
  - `0.0.0.0` 호스트 바인딩 시 미인증 사설망 기기나 타 공인 IP의 무단 서빙 접근 공격 표면을 사전에 방어.
  - `config/server_config.json`의 `allowed_subnets` 목록을 파싱하여 동적으로 CIDR 대역 검증 수행.
- **Alternatives Considered**:
  - OS-level `iptables` / `ufw`: 파이썬 앱 가동 전 수동 설정 필요로 앱 차원의 안전장치 부재 (기각).

### R-003: Subprocess Async Transport Lifecycle Safety (`close_transport`)
- **Decision**: `ProcessManager` 내에 `close_transport()`를 명시화하고, `asyncio.sleep(0.1)` 이벤트 루프 마이크로 틱 양보와 함께 `stop_process()`에 Async Context Manager 지원 추가.
- **Rationale**:
  - Python `asyncio.create_subprocess_exec()`로 실행된 프로세스는 종료 시 transport close가 되지 않으면 `BaseSubprocessTransport.__del__` 콜백이 폐쇄된 이벤트 루프에서 실행되어 `RuntimeError: Event loop is closed`를 유발함.
- **Alternatives Considered**:
  - `warnings.filterwarnings("ignore")`: 증상 은폐 정책으로 컨스티튜션 원칙 위반 (기각).

### R-004: Singleton `httpx.AsyncClient` Connection Pool Management
- **Decision**: FastAPI `app.state.http_client` 및 `inference_api.py` 내 싱글톤 커넥션 풀 패턴을 정립하고, `config/server_config.json`의 `connection_pool` 매개변수(`max_keepalive_connections: 20`, `max_connections: 100`)와 연동.
- **Rationale**:
  - 요청마다 `httpx.AsyncClient()`를 개별 생성/소멸하는 행위는 TCP 커넥션 핸들 누수(Connection Leak) 및 RAG/Agent 병렬 요청 시 소켓 고갈(Socket Exhaustion)을 유발함.

### R-005: Systemd Unit File Integration for Linux Production
- **Decision**: `scripts/vllm_serv.service` 템플릿 파일 생성 및 `setup.sh`를 통해 시스템 서비스 등록 가이드 추가.
- **Rationale**:
  - `nohup` 백그라운드 프로세스의 수동 제어 한계를 극복하고 Linux OS 차원의 자동 재시작 및 런타임 수명주기 보장.
