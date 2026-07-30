# Implementation Plan: 클라이언트 요청 트레이싱 및 상세 감사 로그 시스템 (023-client-request-logging)

**Branch**: `023-client-request-logging` | **Date**: 2026-07-30 | **Spec**: [spec.md](file:///home/dev/storage/vllm_serv/specs/023-client-request-logging/spec.md)

**Input**: Feature specification from `/specs/023-client-request-logging/spec.md`

## Summary

LLM 서빙 환경에서 클라이언트별 요청을 추적하고 오작동 및 장애 원인을 규명하기 위한 **클라이언트 요청 감사 로깅 및 API Key 관리 시스템**을 구현합니다.
FastAPI 미들웨어 기반으로 비동기 큐 로깅(`QueueHandler`/`QueueListener`)을 구현하여 디스크 쓰기 블로킹 없이 2ms 이하 지연 오버헤드(SC-003)를 보장하고, `logs/access.log` 및 `logs/error.log`에 `X-Request-ID` (UUIDv4), 클라이언트 IP(`X-Forwarded-For`), User-Agent, OpenAI `"user"` 필드, 마스킹된 API Key(`sk-***key1`)를 종합 수록합니다.
또한 기존 `/dashboard` 웹 대시보드 UI에 Admin Secret 인증 기반 "API Key 관리" 탭을 통합하여 웹 UI, REST API (`/v1/admin/api-keys`), CLI를 통해 클라이언트 인가 키를 발급·삭제·관리합니다.

## Technical Context

**Language/Version**: Python 3.12 (uv package manager)

**Primary Dependencies**: FastAPI, Uvicorn, Pydantic, standard `logging.handlers` (`QueueHandler`, `RotatingFileHandler`)

**Storage**: `config/server_config.json` (API Key SHA-256 해시 & 마스킹 정보 저장), `logs/access.log`, `logs/error.log`

**Testing**: `pytest`, `httpx` (AsyncTestClient)

**Target Platform**: Linux Server (Intel Xeon / Ubuntu)

**Project Type**: Python Web Service (FastAPI Server + Web Dashboard UI)

**Performance Goals**: 로깅 미들웨어 추가 처리 지연시간 < 2ms (SC-003), 대시보드 키 발급 응답 < 500ms (SC-004)

**Constraints**: `RotatingFileHandler` 10MB x 5개 파일 로테이션 (FR-004), API Key 원본은 1회만 화면 노출 후 해시 저장

**Scale/Scope**: 4개 모듈 (`src/core/client_logger.py`, `src/core/api_key_manager.py`, `src/api/server.py` 미들웨어 & REST API, `src/dashboard/` 웹 UI)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 계획서가 한국어로 작성되었는가? (언어 정책)
- [x] 테스트 코드 작성 계획이 포함되어 있는가? (테스트 필수 원칙: `test_client_access_logger.py`, `test_api_key_manager.py`, `test_admin_api.py`)
- [x] 작업의 종료 조건(Definition of Done)이 명확히 정의되었는가? (종료 조건 명확화 원칙: spec.md 내 DoD-001 ~ DoD-007)

## Project Structure

### Documentation (this feature)

```text
specs/023-client-request-logging/
├── plan.md              # 이 문서 (구현 계획서)
├── research.md          # 비동기 로깅, SHA-256 해시 저장, 클라이언트 식별 연구
├── data-model.md        # AccessLogEntry, ErrorLogEntry, ApiKeyEntity 스키마
├── quickstart.md        # 검증 및 테스트 가이드
└── contracts/
    └── api_contracts.md # Admin API (/v1/admin/*) 인터페이스 명세
```

### Source Code (repository root)

```text
src/
├── core/
│   ├── client_logger.py      # 비동기 큐 기반 ClientAccessLogMiddleware & QueueListener
│   ├── api_key_manager.py    # SHA-256 기반 API Key 생성/검증/마스킹 & storage 관리
│   └── config_manager.py     # server_config.json 설정 연동
├── api/
│   └── server.py             # FastAPI 라우터, 로깅 미들웨어 등록, /v1/admin/* 엔드포인트
└── dashboard/                # HTML/JS/CSS 웹 대시보드 UI (API Key 관리 탭 통합)

tests/
├── unit/
│   ├── test_client_access_logger.py # 로깅 미들웨어 & X-Request-ID 단위 테스트
│   ├── test_api_key_manager.py     # API Key 생성/해시검증/마스킹 단위 테스트
│   └── test_admin_api.py           # Admin Secret 인가 & CRUD REST API 단위 테스트
└── integration/
    └── test_logging_pipeline.py    # E2E 엑세스/에러 감사 로그 수록 통합 테스트
```

**Structure Decision**: 기존 `src/core/`, `src/api/server.py`, `tests/` 단일 프로젝트 구조에 맞춰 `client_logger.py` 및 `api_key_manager.py` 모듈을 모듈화하여 추가합니다.

## Complexity Tracking

> **Violations**: 없음 (헌법 가이드라인 100% 준수)
