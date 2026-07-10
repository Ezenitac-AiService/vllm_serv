---
description: "Task list template for feature implementation"
---

# Tasks: llama.cpp 기반 Gemma4 모델군(2B/4B/12B) 양자화 서비스

**Input**: Design documents from `/specs/001-vllm-gemma4-qat/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are MANDATORY - implementation without tests is prohibited.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Initialize Python environment and create dependencies in `requirements.txt`
- [x] T002 [P] Create project structure directories (`src/core`, `src/api`, `src/scripts`, `tests/unit`, `tests/integration`)
- [x] T003 [P] Configure pytest infrastructure in `tests/conftest.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create configuration module (`ModelConfig`) in `src/core/config.py`
- [x] T005 [P] Implement HuggingFace GGUF model downloader script in `src/scripts/download_models.py`
- [x] T006 [P] Implement `llama_manager.py` (Llama instance loading/unloading wrapper) in `src/core/llama_manager.py`
- [x] T007 Write unit tests for `llama_manager.py` logic in `tests/unit/test_manager.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - 모델 추론 서비스 제공 (Priority: P1) 🎯 MVP

**Goal**: 선택된 메인 모델(또는 기본 12B 모델)을 로드하고 `/v1/chat/completions` API를 통해 OpenAI 호환 텍스트 생성을 안정적으로 제공합니다.

**Independent Test**: 터미널에서 서버를 띄우고 `curl`을 통해 텍스트 생성 응답이 4K 컨텍스트 제한 내에서 성공하는지 확인.

### Tests for User Story 1 (MANDATORY) ⚠️

- [x] T008 [US1] Integration test for `/v1/chat/completions` endpoint in `tests/integration/test_api_chat.py`

### Implementation for User Story 1

- [x] T009 [US1] Create FastAPI application setup in `src/api/server.py`
- [x] T010 [US1] Implement text generation endpoint (`/v1/chat/completions`) in `src/api/routes.py`
- [x] T011 [US1] Add basic error handling for OOM or invalid inputs in `src/api/routes.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - 모델 성능 사전 평가 및 동적 전환 (Priority: P2)

**Goal**: 2B/4B/12B 모델 벤치마크 기능을 스크립트로 제공하고, 서버 런타임에 모델을 동적으로 교체할 수 있는 API를 제공합니다.

**Independent Test**: `benchmark.py` 스크립트를 실행하여 3가지 모델의 VRAM/TPOT를 확인하고, 서버 구동 중 전환 API를 호출해 활성 모델이 교체되는지 확인합니다.

### Tests for User Story 2 (MANDATORY) ⚠️

- [x] T012 [P] [US2] Integration test for model switch endpoint in `tests/integration/test_api_switch.py`

### Implementation for User Story 2

- [x] T013 [P] [US2] Implement benchmarking script (`BenchmarkResult` tracking) in `src/scripts/benchmark.py`
- [x] T014 [US2] Implement model switch API endpoint (`/api/models/switch`) in `src/api/routes.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T015 [P] Create `README.md` adapting the `quickstart.md` scenarios for end users
- [x] T016 Run all quickstart scenarios to confirm OOM prevention and performance requirements

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed sequentially in priority order (P1 → P2)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2)
- **User Story 2 (P2)**: Can start after Foundational (Phase 2)

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel
- T012 and T013 in Phase 4 can be worked on in parallel

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
