# Tasks: 클라이언트 요청 트레이싱 및 상세 감사 로그 시스템 (023-client-request-logging)

**Input**: Design documents from `/specs/023-client-request-logging/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api_contracts.md, quickstart.md

**Tests**: Tests are MANDATORY per constitution (II. 테스트 필수 원칙) - written and verified using `uv run pytest`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [x] [TaskID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5, US6)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify dependencies, environment setup, and data models

- [x] T001 Verify project structure and spec alignment in `specs/023-client-request-logging/plan.md`
- [x] T002 [P] Create `AccessLogEntry`, `ErrorLogEntry`, `ApiKeyEntity`, and `AdminSessionState` Pydantic models in `src/core/client_logger.py` and `src/core/api_key_manager.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core logging infrastructure and config integration required before middleware implementation

- [x] T003 Implement `QueueHandler` / `QueueListener` asynchronous logger setup in `src/core/client_logger.py`
- [x] T004 Extend `src/core/config_manager.py` to support `api_key_enabled`, `api_keys`, and `admin_secret` options in `server_config.json`

---

## Phase 3: User Story 1 & 2 - 클라이언트 엑세스 감사 로깅 및 X-Request-ID 에러 추적 (Priority: P1) 🎯 MVP

**Goal**: 모든 HTTP 요청에 UUIDv4 `X-Request-ID` 부여, `logs/access.log`에 클라이언트 IP/소요시간/모델/User-Agent 기록, 4xx/5xx 예외 발생 시 `logs/error.log`에 에러 정보 수록

**Independent Test**: API 요청 전송 후 `logs/access.log` 항목 생성 확인 및 `X-Request-ID` 헤더 반환 검증

### Tests for User Story 1 & 2

- [x] T005 [P] [US1] Write unit test for `ClientAccessLogMiddleware` and `X-Request-ID` header generation in `tests/unit/test_client_access_logger.py`
- [x] T006 [P] [US2] Write unit test for 4xx/5xx error logging to `logs/error.log` in `tests/unit/test_client_access_logger.py`

### Implementation for User Story 1 & 2

- [x] T007 [US1] Implement `ClientAccessLogMiddleware` in `src/api/middleware/client_access_logger.py` to intercept requests, extract client identity (IP, OpenAI `user` field, User-Agent), compute latency (ms), and output to `logs/access.log`
- [x] T008 [US2] Add `X-Request-ID` UUIDv4 generation to response headers and exception logging handler to `logs/error.log` in `src/api/middleware/client_access_logger.py`
- [x] T009 [US1] Register `ClientAccessLogMiddleware` in FastAPI server initialization in `src/api/server.py`
- [x] T010 [US1] Verify logging middleware execution via `uv run pytest tests/unit/test_client_access_logger.py`

---

## Phase 4: User Story 3 - 로그 파일 용량 관리 및 자동 로테이션 (Priority: P2)

**Goal**: `RotatingFileHandler`를 적용하여 10MB 크기 기준 최대 5개 파일로 자동 로테이션 수행

**Independent Test**: 로깅 억제 및 파일 핸들러 설정을 검증하여 10MB 분할 로테이션 동작 확인

### Tests for User Story 3

- [x] T011 [P] [US3] Write unit test verifying `RotatingFileHandler` configuration (10MB, max 5 backup files) in `tests/unit/test_client_access_logger.py`

### Implementation for User Story 3

- [x] T012 [US3] Configure `RotatingFileHandler` with 10MB maxBytes and 5 backupCount for both `access.log` and `error.log` in `src/core/client_logger.py`
- [x] T013 [US3] Verify log rotation tests via `uv run pytest tests/unit/test_client_access_logger.py`

---

## Phase 5: User Story 4 - API Key 기본 검증 및 마스킹 감사 로깅 (Priority: P2)

**Goal**: `Authorization: Bearer <KEY>` 인가 검증 수행 및 마스킹 처리된 키(`sk-***key1`)를 감사 로그에 수록

**Independent Test**: 유효하지 않은 API Key로 요청 시 401 Unauthorized 반환 및 유효 요청 시 마스킹된 키 `access.log` 수록 확인

### Tests for User Story 4

- [x] T014 [P] [US4] Write unit tests for API Key verification and masking logic in `tests/unit/test_api_key_manager.py`

### Implementation for User Story 4

- [x] T015 [US4] Implement `ApiKeyManager` in `src/core/api_key_manager.py` to handle SHA-256 key hashing, Bearer token verification, and key masking (`sk-***<last_4>`)
- [x] T016 [US4] Integrate API Key verification check and masked key logging into `ClientAccessLogMiddleware` in `src/api/middleware/client_access_logger.py`
- [x] T017 [US4] Verify API Key authentication tests via `uv run pytest tests/unit/test_api_key_manager.py`

---

## Phase 6: User Story 6 - Admin Secret (관리자 비밀번호) 기반 인가 보호 (Priority: P1)

**Goal**: `admin_secret` 자격 증명을 검증하여 관리자 대시보드 및 `/v1/admin/*` API 접근 차단 및 보호

**Independent Test**: 잘못된 `X-Admin-Secret`으로 관리자 API 호출 시 403 Forbidden 반환 확인

### Tests for User Story 6

- [x] T018 [P] [US6] Write unit tests for Admin Secret authorization in `tests/unit/test_admin_api.py`

### Implementation for User Story 6

- [x] T019 [US6] Implement `verify_admin_secret` dependency and session token verification in `src/core/api_key_manager.py`
- [x] T020 [US6] Protect admin endpoints (`/v1/admin/*`) with Admin Secret authorization in `src/api/routes/admin_api.py`
- [x] T021 [US6] Verify Admin authentication tests via `uv run pytest tests/unit/test_admin_api.py`

---

## Phase 7: User Story 5 - 웹 대시보드 UI 및 REST API/CLI 기반 API Key 발급·관리 (Priority: P2)

**Goal**: `/dashboard` 웹 UI에 "API Key 관리" 탭 추가, 백엔드 CRUD API (`/v1/admin/api-keys`) 제공

**Independent Test**: 대시보드 UI에서 `[새 API Key 생성]` 클릭 시 1회성 raw key 노출 및 `server_config.json` 저장 확인

### Tests for User Story 5

- [x] T022 [P] [US5] Write contract integration tests for `/v1/admin/api-keys` endpoints in `tests/unit/test_admin_api.py`

### Implementation for User Story 5

- [x] T023 [US5] Implement REST API endpoints (`GET /v1/admin/api-keys`, `POST /v1/admin/api-keys`, `DELETE /v1/admin/api-keys/{key_id}`) in `src/api/routes/admin_api.py`
- [x] T024 [US5] Update `/dashboard` HTML/JS in `src/api/static/index.html` and `src/api/static/app.js` to add "API Key Management" UI tab with login modal, key creation, and revocation list
- [x] T025 [US5] Add CLI key management interface in `src/core/api_key_manager.py`
- [x] T026 [US5] Verify Admin API & Web UI integration via `uv run pytest tests/unit/test_admin_api.py`

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: E2E integration testing, quickstart verification, and full regression test execution

- [x] T027 [P] Write E2E integration test for logging and key management in `tests/integration/test_logging_pipeline.py`
- [x] T028 Run quickstart verification scenarios in `specs/023-client-request-logging/quickstart.md`
- [x] T029 Execute full test suite with `uv run pytest tests/` to confirm zero regressions across all 135 tests
