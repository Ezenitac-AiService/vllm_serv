# Tasks: 서버 헬스진단 스크립트 정밀화 및 8082 대시보드 연동 복구 (075-fix-server-health-diagnostics)

**Input**: Design documents from `/specs/075-fix-server-health-diagnostics/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: 헌법 VII조(의무적 회귀 테스트) 및 실체적 TDD 원칙(헌법 II/III조, Zero Mock)에 의거하여 통합 진단 수렴 검증 테스트 포함.

**Organization**: 각 과제는 유저 스토리(US1, US2)별로 독립 수록되어 독립 구현 및 검증 가능.

## Format: `- [ ] [ID] [P?] [Story?] Description with file path`

- **[P]**: 병렬 수행 가능 (다른 파일, 미완료 과제에 대한 의존성 없음)
- **[Story]**: 해당 유저 스토리 (US1, US2)

---

## Phase 1: Setup (공통 환경 및 기반)

**Purpose**: 진단 스크립트 및 서버 가동 파일 구조 점검

- [x] T001 Inspect current probe implementations in `scripts/diagnose_server_health.py`
- [x] T002 Inspect process management logic in `start_server.sh` and `status_server.sh`

---

## Phase 2: Foundational (차단적 전제 과제)

**Purpose**: 진단 헬스체크 기반 포트 및 엔드포인트 수신 기본 구조 정비

- [x] T003 Clean up network socket timeout handling in `scripts/diagnose_server_health.py`

**Checkpoint**: Foundation ready - 유저 스토리별 작업 진행 가능

---

## Phase 3: User Story 1 - `/v1/chat/completions` API 헬스 프로브 정밀화 (Priority: P1) 🎯 MVP

**Goal**: Pydantic 스키마 잔재를 완전히 제거하고 파이썬 기본 딕셔너리(`dict`) 페이로드 기반으로 `/v1/chat/completions` 헬스 프로브를 리팩토링하여 200 OK 정밀 수렴 달성

**Independent Test**: `uv run python scripts/diagnose_server_health.py` 실행 시 `/v1/chat/completions: ✅ 200 OK` 출력

### Tests for User Story 1

- [x] T004 [P] [US1] Create integration test for health diagnostics in `tests/integration/test_server_health_diagnostics.py`

### Implementation for User Story 1

- [x] T005 [US1] Refactor `/v1/chat/completions` probe to use python dict payload in `scripts/diagnose_server_health.py`
- [x] T006 [US1] Verify chat completions probe returns 200 OK via `uv run python scripts/diagnose_server_health.py`

**Checkpoint**: User Story 1 (MVP) 독립 수렴 검증 완료

---

## Phase 4: User Story 2 - Port 8082 웹 대시보드 구동 및 E2E 렌더링 정상화 (Priority: P2)

**Goal**: Port 8082 웹 대시보드 원스톱 가동, UFW 방화벽 규칙 자동 등록 및 진단 결과 `Port 8082_dashboard: ✅ OPEN` / `🖥️ 웹 대시보드 E2E 렌더링 : ✅ ON` 달성

**Independent Test**: `uv run python scripts/diagnose_server_health.py` 실행 시 8082 포트 및 대시보드 E2E가 ✅ OPEN / ✅ ON으로 표시됨

### Tests for User Story 2

- [x] T007 [P] [US2] Create integration test for 8082 dashboard binding in `tests/integration/test_dashboard_port_binding.py`

### Implementation for User Story 2

- [x] T008 [US2] Update `scripts/setup.sh` to register `ufw allow 8081/tcp` and `ufw allow 8082/tcp` rules in `scripts/setup.sh`
- [x] T009 [US2] Update `start_server.sh` to launch Port 8082 Web Dashboard in `start_server.sh`
- [x] T010 [US2] Update `status_server.sh` to report Port 8082 binding status in `status_server.sh`
- [x] T011 [US2] Verify Port 8082 dashboard rendering and open status via `uv run python scripts/diagnose_server_health.py`

**Checkpoint**: User Story 1 및 2 완결

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: ALL GREEN (SYSTEM HEALTHY) 종합 진단 검증 및 전체 회귀 테스트 수행

- [x] T012 [P] Verify ALL GREEN output (`STATUS: 🎉 SYSTEM HEALTHY`) in `scripts/diagnose_server_health.py`
- [x] T013 Execute full suite regression test via `uv run pytest` per Constitution Article VII

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup & Foundational (Phase 1 & 2)**: 즉시 시작 가능
- **User Story 1 (Phase 3)**: Foundational 완료 후 진행 (`diagnose_server_health.py` 리팩토링)
- **User Story 2 (Phase 4)**: US1 완료 후 진행 (`start_server.sh`, `setup.sh`, `status_server.sh` 연동)
- **Polish (Phase 5)**: 모든 유저 스토리 완성 후 종합 실측 검증

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & 2 (Setup & Foundational)
2. Complete Phase 3 (User Story 1 - `/v1/chat/completions` 프로브 정밀화)
3. **Validate**: `uv run python scripts/diagnose_server_health.py`로 200 OK 수신 확인

### Full Delivery

1. Setup + Foundational -> US1 (MVP Chat Probe) -> US2 (Dashboard Port 8082) -> SYSTEM HEALTHY ALL GREEN
2. Full Suite Regression Test: `uv run pytest`
