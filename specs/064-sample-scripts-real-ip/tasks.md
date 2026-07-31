# Tasks: 샘플 스크립트 실 IP 동적 자동 감지(192.168.0.x / 10.0.0.x / 듀얼 랜포트 지원) 및 연동 설정 개선

**Input**: Design documents from `/specs/064-sample-scripts-real-ip/`

**Prerequisites**: [plan.md](file:///home/dev/storage/vllm_serv/specs/064-sample-scripts-real-ip/plan.md), [spec.md](file:///home/dev/storage/vllm_serv/specs/064-sample-scripts-real-ip/spec.md), [research.md](file:///home/dev/storage/vllm_serv/specs/064-sample-scripts-real-ip/research.md), [data-model.md](file:///home/dev/storage/vllm_serv/specs/064-sample-scripts-real-ip/data-model.md), [quickstart.md](file:///home/dev/storage/vllm_serv/specs/064-sample-scripts-real-ip/quickstart.md)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and NetworkDetector module verification

- [x] T001 Verify `src/core/network_detector.py` interface scanning and active LAN IP extraction API

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core dynamic server host resolution helper in `samples/common.py`

- [x] T002 Update `samples/common.py` `get_server_host()` helper to integrate `NetworkDetector.get_active_lan_ips()` with `SERVER_HOST` environment variable priority and dual-LAN filtering

**Checkpoint**: Foundation ready - user story implementation can begin in parallel

---

## Phase 3: User Story 1 - 듀얼 랜포트 & 다중 서브넷(192.168.0.x / 10.0.0.x) 동적 IP 감지 헬퍼 (`samples/common.py`) (Priority: P1) 🎯 MVP

**Goal**: Eliminate IP hardcoding and dynamically resolve host LAN IP across 192.168.0.x and 10.0.0.x platforms.

**Independent Test**: Run `uv run python -c "from samples.common import get_server_host; print(get_server_host())"` and verify valid LAN IP host URL returned without hardcoding.

### Tests for User Story 1 ⚠️

- [x] T003 [P] [US1] Write unit test for `get_server_host()` dynamic IP resolution in `tests/unit/test_network_detector.py`

### Implementation for User Story 1

- [x] T004 [US1] Implement dynamic LAN IP fallback in `samples/common.py` `check_server_health()`

**Checkpoint**: User Story 1 fully functional — dynamic LAN IP detection verified.

---

## Phase 4: User Story 2 - 전체 샘플 스크립트 실 IP 동적 적용 (`sample_01` ~ `sample_05`) (Priority: P2)

**Goal**: Replace hardcoded `127.0.0.1` strings in `sample_01_chat.py` ~ `sample_05_structured_output.py` with `get_server_host()`.

**Independent Test**: Run `uv run python samples/sample_01_chat.py` and verify HTTP 200 OK response using detected server host IP.

### Implementation for User Story 2

- [x] T005 [P] [US2] Update `samples/sample_01_chat.py` to use `SERVER_HOST = get_server_host()`
- [x] T006 [P] [US2] Update `samples/sample_02_model_params.py` to use `SERVER_HOST = get_server_host()`
- [x] T007 [P] [US2] Update `samples/sample_03_embedding.py` to use `SERVER_HOST = get_server_host()`
- [x] T008 [P] [US2] Update `samples/sample_04_reranking.py` to use `SERVER_HOST = get_server_host()`
- [x] T009 [P] [US2] Update `samples/sample_05_structured_output.py` to use `SERVER_HOST = get_server_host()`

**Checkpoint**: User Story 2 fully functional — all 5 sample scripts using dynamic server host IP.

---

## Phase 5: User Story 3 - 단위/통합 회귀 테스트 수트 검증 (Priority: P3)

**Goal**: Ensure `tests/unit/test_sample_scripts.py` and `tests/unit/test_network_detector.py` pass with dynamic host resolution.

**Independent Test**: Run `uv run pytest tests/unit/test_sample_scripts.py tests/unit/test_network_detector.py` and verify 100% Green Pass.

### Tests for User Story 3 ⚠️

- [x] T010 [P] [US3] Update `tests/unit/test_sample_scripts.py` healthcheck test to assert dynamic server host
- [x] T011 [P] [US3] Add unit test for unassigned dual-LAN port filtering in `tests/unit/test_network_detector.py`

**Checkpoint**: User Story 3 fully functional — test suite verifying dynamic IP host binding.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Quickstart validation and full regression test suite execution

- [x] T012 Run quickstart validation scenarios documented in `quickstart.md`
- [x] T013 Run full regression test suite (`uv run pytest`) to ensure 100% Green Pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1) → User Story 2 (P2) → User Story 3 (P3)
- **Polish (Phase 6)**: Depends on all user stories being complete

### Parallel Opportunities

- T003, T005, T006, T007, T008, T009, T010, T011 can run in parallel (different files, no dependencies)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup (Phase 1) and Foundational (Phase 2)
2. Complete User Story 1 (Phase 3)
3. Validate dynamic LAN IP resolution helper (`samples/common.py`)

### Incremental Delivery

1. Deliver MVP (`get_server_host()`)
2. Apply dynamic IP to `sample_01` ~ `sample_05`
3. Update regression unit tests and run `uv run pytest`
