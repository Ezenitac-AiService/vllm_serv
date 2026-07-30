# Tasks: 2026년 7월 최신 기술 기준 서빙 파이프라인 리팩토링 및 현대화 분석 (027-architecture-refactoring-analysis)

**Input**: Design documents from `/specs/027-architecture-refactoring-analysis/`

**Prerequisites**: [plan.md](file:///home/dev/storage/vllm_serv/specs/027-architecture-refactoring-analysis/plan.md), [spec.md](file:///home/dev/storage/vllm_serv/specs/027-architecture-refactoring-analysis/spec.md), [research.md](file:///home/dev/storage/vllm_serv/specs/027-architecture-refactoring-analysis/research.md), [data-model.md](file:///home/dev/storage/vllm_serv/specs/027-architecture-refactoring-analysis/data-model.md), [quickstart.md](file:///home/dev/storage/vllm_serv/specs/027-architecture-refactoring-analysis/quickstart.md)

**Tests**: 테스트 코드는 헌장 II원칙(테스트 주도 개발 및 품질 보증)에 따라 리팩토링 전후 100% pytest 통과를 지속 검증합니다.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [TaskID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (`[US1]`, `[US2]`, `[US3]`)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project configuration layout & schema verification

- [x] T001 Verify project structure and specification files at `specs/027-architecture-refactoring-analysis/`
- [x] T002 Update `config/server_config.json` schema to include optional `speculative_decoding` and `structured_output` settings

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Base test structures and architecture verification scaffolding

- [x] T003 [P] Create unit test scaffold for 2026 SOTA serving refactoring features in `tests/unit/test_sota_serving_refactoring.py`

**Checkpoint**: Foundation ready - test harnesses and schema ready.

---

## Phase 3: User Story 1 - 2026년 최신 LLM 서빙 동향 분석 및 리팩토링 타겟 도출 (Priority: P1) 🎯 MVP

**Goal**: Analyze 2026 SOTA LLM serving trends (FlashAttention-3, GGML CUDA kernels, Pydantic v2) and document refactoring roadmap.

**Independent Test**: `specs/027-architecture-refactoring-analysis/research.md` contains comprehensive refactoring analysis.

- [x] T004 [P] [US1] Analyze GGML CUDA kernel acceleration & FlashAttention-3 integration in `src/core/process_manager.py`
- [x] T005 [P] [US1] Analyze model catalog draft model pairings in `config/model_catalog.json` and `src/core/config_manager.py`
- [x] T006 [US1] Document 2026 SOTA refactoring architecture findings in `specs/027-architecture-refactoring-analysis/research.md`

**Checkpoint**: User Story 1 (SOTA Analysis) is complete.

---

## Phase 4: User Story 2 - Speculative Decoding 및 구조화된 출력(Structured Output) 엔진 모듈화 (Priority: P2)

**Goal**: Design and implement OpenAI `response_format` parser and Speculative Decoding CLI propagator.

**Independent Test**: OpenAI requests with `response_format` parse correctly and `uv run pytest tests/` passes 100%.

- [x] T007 [P] [US2] Implement OpenAI `response_format` parser and JSON Schema converter in `src/api/routes/inference_api.py`
- [x] T008 [P] [US2] Implement `SpeculativeDecodingConfig` data model and CLI argument propagator in `src/core/process_manager.py`
- [x] T009 [US2] Update `src/core/llama_manager.py` to support speculative draft model pairing and structured output routing

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final verification, import audit, and test execution

- [x] T010 [P] Verify 100% backward compatibility for standard OpenAI API endpoints (`/v1/models`, `/v1/chat/completions`)
- [x] T011 Run complete pytest test suite (`uv run pytest tests/`) to ensure 100% test pass rate
- [x] T012 Execute quickstart validation scenarios in `specs/027-architecture-refactoring-analysis/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Stories (Phase 3+)**: Depend on Foundational phase completion
  - User Story 1 (P1) -> User Story 2 (P2)
- **Polish (Final Phase)**: Depends on all user stories being complete

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup & Phase 2: Foundational
2. Complete Phase 3: User Story 1 (SOTA Analysis)
3. Complete Phase 4: User Story 2 (Speculative & Structured Output)
4. Complete Phase 5: Polish (`uv run pytest tests/`)
