# Tasks: 002-performance-comparison

**Input**: Design documents from `/specs/002-performance-comparison/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md, quickstart.md

**Tests**: 테스트 코드 작성이 원칙이므로, 모의(Mock)를 제거하고 실제 구동 가능한 단위/통합 테스트를 반영합니다.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: `.env` 기반 환경 구성 및 의존성 주입

- [x] T001 Update `requirements.txt` to include `python-dotenv`
- [x] T002 Configure `python-dotenv` loading in `src/core/config.py`
- [x] T003 Create sample `.env.example` file

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 하드코딩 배제 및 모델 다운로더 최적화

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Refactor `src/scripts/download_models.py` to securely use `HF_TOKEN` from `.env`
- [x] T005 [P] Implement token validation logic in config layer to fast-fail if `HF_TOKEN` is missing

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - 모델 성능 및 VRAM 사용량 비교 (Priority: P1) 🎯 MVP

**Goal**: E2B, E4B, 12B 모델을 로드하여 Short, Medium, 4K Long 프롬프트에 따른 TPOT 및 VRAM 측정

**Independent Test**: `python3 src/scripts/benchmark.py` 실행 시 OOM 여부, 로드 시간, VRAM, TPOT가 정상 출력되어야 함.

### Tests for User Story 1 (MANDATORY) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T006 [P] [US1] Integration test for loading a real model without mock in `tests/integration/test_model_load.py`
- [x] T007 [P] [US1] Unit test for handling OOM exceptions safely in `tests/unit/test_oom_handler.py`

### Implementation for User Story 1

- [x] T008 [US1] Define tiered prompts (Short, Medium, 4K Long) in `src/scripts/benchmark.py`
- [x] T009 [US1] Implement `BenchmarkRunner` to sequentially load models from `config.py` using `llama_manager.py`
- [x] T010 [US1] Integrate `nvidia-smi` or similar tool inside Python to capture peak VRAM during load and inference
- [x] T011 [US1] Measure TPOT(Tokens Per Output Token) and print the BenchmarkResult summary table
- [x] T012 [US1] Add graceful error handling and reporting for `OOM_FAILED` status

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T013 Update README.md with instructions from `quickstart.md`
- [x] T014 Run overall quickstart validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### Parallel Opportunities

- T006, T007 테스트 코드 작성은 서로 병렬 진행 가능
- T013 README 갱신은 US1 진행 중에도 병행 가능
