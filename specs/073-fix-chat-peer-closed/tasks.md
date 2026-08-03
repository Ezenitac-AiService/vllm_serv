# Tasks: Chat Completions API 커넥션 두절 오류 수정 및 파이프라인 안정화

**Input**: Design documents from `/specs/073-fix-chat-peer-closed/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: 헌법 VII조(의무적 회귀 테스트) 및 실체적 TDD 원칙(헌법 II/III조, Zero Mock)에 의거하여 각 유저 스토리별 실측 통합 테스트 포함.

**Organization**: 각 과제는 유저 스토리(US1, US2, US3)별로 독립 수록되어 독립 구현 및 테스트 가능.

## Format: `- [ ] [ID] [P?] [Story?] Description with file path`

- **[P]**: 병렬 수행 가능 (다른 파일, 미완료 과제에 대한 의존성 없음)
- **[Story]**: 해당 유저 스토리 (US1, US2, US3)

---

## Phase 1: Setup (공통 인프라 및 환경)

**Purpose**: 프로젝트 환경 검증 및 스크립트 정합성 확인

- [x] T001 Verify Python virtualenv and packages via `uv` in `.venv/`
- [x] T002 [P] Verify shell script syntax for `status_server.sh`, `start_server.sh`, `stop_server.sh`

---

## Phase 2: Foundational (차단적 전제 과제)

**Purpose**: 모든 유저 스토리가 실행되기 전 완성되어야 하는 핵심 프로토콜 세이프가드 레이어

- [x] T003 [P] Setup integration test harness for ASGI protocol validation in `tests/integration/test_chat_connection.py`
- [x] T004 [P] Implement UTF-8 byte-length encoder utility in `src/core/utils/encoding.py`
- [x] T005 Implement ASGI Content-Length validator & safe response wrapper in `src/core/middleware/protocol_guard.py`

**Checkpoint**: Foundation ready - 유저 스토리별 구현 시작 가능

---

## Phase 3: User Story 1 - Chat Completions API 예제 및 서비스 연결 두절 수정 (Priority: P1) 🎯 MVP

**Goal**: `sample_01_chat.py` 실행 시 `peer closed connection without sending complete message body` 오류를 제거하고 100% 정상 수신 보장

**Independent Test**: `uv run python samples/sample_01_chat.py` 실행 시 `[요청 실패]` 없이 정상적인 답변 JSON Payload 출력 수신

### Tests for User Story 1

- [x] T006 [P] [US1] Create integration test for Chat Completions API connection drop in `tests/integration/test_chat_completions_connection.py`
- [x] T007 [P] [US1] Create contract validation test for OpenAI Chat schema in `tests/contract/test_chat_contract.py`

### Implementation for User Story 1

- [x] T008 [US1] Fix Content-Length header calculation to use exact UTF-8 byte length in `src/api/routes/chat.py`
- [x] T009 [US1] Refactor StreamingResponse to omit static Content-Length and handle chunked EOF in `src/services/llama_service.py`
- [x] T010 [US1] Verify `samples/sample_01_chat.py` execution via `uv run python samples/sample_01_chat.py`

**Checkpoint**: User Story 1 (MVP) 독립 기능 구현 및 수렴 검증 완료

---

## Phase 4: User Story 2 - 모델 파라미터 제어 및 Stop Sequence 생성 중단 안정성 (Priority: P2)

**Goal**: `sample_02_model_params.py` 실행 시 `h11.LocalProtocolError: Too little data for declared Content-Length` 조기 중단 예외 방지

**Independent Test**: `uv run python samples/sample_02_model_params.py` 실행 시 Low Temp 및 Stop Sequence 예제 항목 모두 100% 성공

### Tests for User Story 2

- [x] T011 [P] [US2] Create integration test for Stop sequence and Low Temperature in `tests/integration/test_model_params.py`

### Implementation for User Story 2

- [x] T012 [US2] Implement Stop Sequence truncation EOF handler and buffer flusher in `src/services/llama_service.py`
- [x] T013 [US2] Verify `samples/sample_02_model_params.py` execution via `uv run python samples/sample_02_model_params.py`

**Checkpoint**: User Story 1 및 2 독립 수렴 완료

---

## Phase 5: User Story 3 - 다중 모델(BGE Reranker 8091) 서빙 포트 정상 구동 보장 (Priority: P3)

**Goal**: Reranker 서버 데몬(8091 포트)을 정상 바인딩하고 `status_server.sh` 헬스 체크 동기화

**Independent Test**: `uv run python samples/sample_04_reranking.py` 실행 시 포트 8091 연결 실패 대신 정상 점수 반환 출력

### Tests for User Story 3

- [x] T014 [P] [US3] Create health check integration test for 8081, 8090, 8091 ports in `tests/integration/test_multi_model_ports.py`

### Implementation for User Story 3

- [x] T015 [US3] Update AuxiliaryManager daemon spawner for BGE Reranker v2 M3 on port 8091 in `src/services/auxiliary_manager.py`
- [x] T016 [US3] Update `status_server.sh` and `start_server.sh` for port 8091 monitoring and health check
- [x] T017 [US3] Verify `samples/sample_03_embedding.py` and `samples/sample_04_reranking.py` execution

**Checkpoint**: 모든 유저 스토리 독립 구현 완료

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 품질 다듬기 및 전체 회귀 검증

- [x] T018 [P] Update API documentation and quickstart guide in `specs/073-fix-chat-peer-closed/quickstart.md`
- [x] T019 Execute full suite regression test via `uv run pytest` per Constitution Article VII

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 즉시 시작 가능
- **Foundational (Phase 2)**: Setup 완료 후 진행 - 모든 유저 스토리 차단(Block)
- **User Stories (Phase 3+)**: Foundational 완료 후 진행 (US1 -> US2 -> US3 순차 또는 병열 가능)
- **Polish (Phase 6)**: 모든 유저 스토리 완결 후 진행

### User Story Dependencies

- **User Story 1 (P1)**: Foundational 완료 후 시작 (의존성 없음)
- **User Story 2 (P2)**: Foundational 완료 후 시작 (US1과 독립적으로 검증 가능)
- **User Story 3 (P3)**: Foundational 완료 후 시작 (US1/US2와 독립적으로 검증 가능)

---

## Parallel Execution Opportunities

```bash
# Foundational 병렬 과제:
T003: Setup integration test harness in tests/integration/test_chat_connection.py
T004: Implement UTF-8 byte-length encoder utility in src/core/utils/encoding.py

# User Story 1 병렬 과제:
T006: Create integration test in tests/integration/test_chat_completions_connection.py
T007: Create contract validation test in tests/contract/test_chat_contract.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & 2 (Setup & Foundational)
2. Complete Phase 3 (User Story 1)
3. **Validate**: `uv run python samples/sample_01_chat.py` 실행으로 `peer closed connection` 해결 실측

### Full Delivery

1. Setup + Foundational -> US1 (MVP) -> US2 (Params/Stop) -> US3 (Reranker 8091)
2. Run Full Suite Regression Test: `uv run pytest`
