# Tasks: vLLM 서빙 대시보드 고도화 (037-dashboard-enhancement)

**Input**: Design documents from `/specs/037-dashboard-enhancement/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`  
**Tests**: Unit and API integration tests in `tests/unit/test_dashboard_api.py`

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story mapping ([US1], [US2], [US3], [US4])

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Dashboard static resources and initial structure setup

- [x] T001 Verify project structure and `uv` dependencies in `pyproject.toml`
- [x] T002 Configure static directory binding for `/dashboard` in `src/api/server.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core security middleware and metrics collection foundation

- [x] T003 Implement `x-admin-secret` authentication verifier in `src/api/routes/dashboard_api.py`
- [x] T004 Implement NVML & CPU fallback resource metric collector in `src/core/model_manager.py`
- [x] T005 [P] Setup client access audit logging middleware in `src/api/middleware/client_access_logger.py`

**Checkpoint**: Foundational APIs and security ready - User stories can begin.

---

## Phase 3: User Story 1 - 실시간 GPU/VRAM 및 서빙 메트릭 시각화 (Priority: P1) 🎯 MVP

**Goal**: GPU/VRAM, TTFT, TPOT 실시간 시계열 캔버스 차트 및 90% VRAM 경고 뱃지 제공

**Independent Test**: `http://10.0.0.41:8000/dashboard/` 접속 시 Chart.js 시계열 그래프 실시간 수신 및 VRAM 90% 경고 활성화 검증

### Tests for User Story 1

- [x] T006 [P] [US1] Unit test for `/dashboard/api/stream` SSE metric endpoint in `tests/unit/test_dashboard_api.py`

### Implementation for User Story 1

- [x] T007 [P] [US1] Create Chart.js real-time canvas chart layout in `src/api/static/index.html`
- [x] T008 [P] [US1] Style Glassmorphism dark mode metric cards and warning badges in `src/api/static/style.css`
- [x] T009 [US1] Implement SSE EventSource metric listener & Chart.js renderer in `src/api/static/app.js`

**Checkpoint**: User Story 1 MVP fully functional and testable independently.

---

## Phase 4: User Story 2 - 플랫폼 프로필 동적 모델 전환 및 컨텍스트 제어 (Priority: P2)

**Goal**: 플랫폼 프로필 기반 모델 동적 로딩, 컨텍스트 스케일링 및 Admin Secret 401 보안 검증

**Independent Test**: 모델 제어 드롭다운에서 모델 선택 후 적용 시 Admin Secret 인증 패널 표출 및 오프로드/전환 동작 확인

### Tests for User Story 2

- [x] T010 [P] [US2] Unit test for `/dashboard/api/capabilities` and `/dashboard/api/apply` in `tests/unit/test_dashboard_api.py`
- [x] T011 [P] [US2] Unit test for unauthenticated state-mutating requests returning 401 Unauthorized in `tests/unit/test_dashboard_api.py`

### Implementation for User Story 2

- [x] T012 [US2] Update `/dashboard/api/capabilities` endpoint in `src/api/routes/dashboard_api.py` to return platform profile filtered models
- [x] T013 [US2] Update `/dashboard/api/apply` and `/dashboard/api/unload` endpoints to enforce `x-admin-secret` authentication
- [x] T014 [US2] Update UI model dropdown & presets dynamic generation logic in `src/api/static/app.js`

**Checkpoint**: User Story 1 and 2 work independently with full Admin Secret protection.

---

## Phase 5: User Story 4 - 인터랙티브 LLM 플레이그라운드 & 실시간 성능 실측 (Priority: P2)

**Goal**: 대시보드 내 프롬프트 테스트 스트리밍, TTFT/tok s 실측 지표 및 Code Export 제공

**Independent Test**: Playground 탭에서 질의 제출 시 스트리밍 텍스트와 하단 TTFT(ms), tok/s 뱃지 및 Code Export 모달 동작 검증

### Tests for User Story 4

- [x] T015 [P] [US4] Integration test for Playground inference test execution in `tests/unit/test_dashboard_api.py`

### Implementation for User Story 4

- [x] T016 [P] [US4] Create Playground tab UI (System Prompt, Sliders, Output Card, Code Export modal) in `src/api/static/index.html`
- [x] T017 [US4] Implement Playground streaming client, TTFT(ms) & tok/s calculator in `src/api/static/app.js`
- [x] T018 [US4] Add cURL and Python OpenAI SDK code export generator in `src/api/static/app.js`

**Checkpoint**: LLM Playground panel fully functional.

---

## Phase 6: User Story 3 - 클라이언트 접속 로그 및 서브넷 접근 감사 (Priority: P3)

**Goal**: 최근 클라이언트 접속 IP, 서브넷 차단 여부 및 HTTP 상태 코드 타임라인 뷰 제공

**Independent Test**: 감사 로그 탭에서 최근 100건의 API 호출 내역이 정렬되어 표시되는지 확인

### Tests for User Story 3

- [x] T019 [P] [US3] Unit test for audit log JSON retrieval in `tests/unit/test_dashboard_api.py`

### Implementation for User Story 3

- [x] T020 [P] [US3] Create Audit Log timeline table UI in `src/api/static/index.html`
- [x] T021 [US3] Implement Audit Log retrieval endpoint `/dashboard/api/audit` in `src/api/routes/dashboard_api.py`
- [x] T022 [US3] Implement Audit Log table auto-refresh in `src/api/static/app.js`

**Checkpoint**: All 4 user stories independently testable and operational.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Cross-cutting improvements and test suite validation

- [x] T023 [P] Add mobile responsive breakpoint styles in `src/api/static/style.css`
- [x] T024 Execute full test suite `uv run pytest tests/unit/test_dashboard_api.py -v`
- [x] T025 Run quickstart validation scenarios in `specs/037-dashboard-enhancement/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Blocks all user stories.
- **User Stories (Phases 3-6)**: Depend on Phase 2 completion. Can proceed sequentially (US1 → US2 → US4 → US3).
- **Polish (Phase 7)**: Depends on completion of user stories.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) & Phase 2 (Foundational)
2. Complete Phase 3 (User Story 1)
3. Validate Chart.js real-time metrics streaming
