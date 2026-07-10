# Tasks: 컨텍스트 윈도우 스케일링 벤치마크

**Input**: Design documents from `/specs/003-context-scaling/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create benchmark script file `src/scripts/benchmark_context_scaling.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 Implement VRAM peak memory monitoring function using `nvidia-smi`
- [x] T003 [P] Implement base JSONL logger class for writing to `specs/003-context-scaling/results.jsonl`
- [x] T004 Set up `LlamaManager` initialization and model unloading pipeline

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - 컨텍스트 길이에 따른 상세 성능 프로파일링 (Priority: P1) 🎯 MVP

**Goal**: e2b, e4b, 12b 모델을 대상으로 8K부터 1K 단위로 스케일링하며 VRAM, TTFT, TPOT, Accuracy를 측정하는 벤치마크 실행

**Independent Test**: 단일 모델(e2b)에 대해 8K 컨텍스트만 1회 실행하여 로깅과 Needle in a Haystack 검증이 정상 동작하는지 테스트

### Implementation for User Story 1

- [x] T005 [P] [US1] Implement `generate_haystack_with_needle` function (synthetic Paul Graham text generator with target needle insertion)
- [x] T006 [P] [US1] Implement metric calculation logic (TTFT, TPOT, and Exact Match Accuracy for the needle)
- [x] T007 [US1] Implement the scaling loop (Start at 8K, increment by 1K) in `src/scripts/benchmark_context_scaling.py`
- [x] T008 [US1] Implement graceful exit conditions (OOM Catching and TTFT > 60s timeout handling)
- [x] T009 [US1] Integrate LlamaManager generate call with the loop and metrics logger
- [x] T010 [US1] Add outer loop to iterate over all target models (`gemma4-2b`, `gemma4-4b`, `gemma4-12b`)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T011 Run `quickstart.md` validation to ensure the entire benchmark suite runs as documented

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Parallel Opportunities

- T003 (JSONL logger) can be implemented in parallel with T002 (VRAM monitoring).
- T005 (Needle generator) and T006 (Metric logic) can be implemented in parallel within Phase 3.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently by running `quickstart.md` scenario.
