# Tasks: 6-Model Comprehensive Benchmark Report, Qualitative Answer Comparison & Context Window Scaling Enhancement

**Input**: Design documents from `/specs/013-enhance-benchmark-report/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included per TDD and Quality Assurance principles.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- File paths are explicitly specified in all task descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and feature environment verification

- [ ] T001 Verify project environment & feature 013 artifacts in specs/013-enhance-benchmark-report/plan.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [ ] T002 Extend QualitativeSampleComparison, ContextScalingMetric, and ComprehensiveQualityReportMetric entities in src/eval/quality_evaluator.py and scripts/benchmark_quality.py
- [ ] T003 [P] Create contract validator for specs/013-enhance-benchmark-report/contracts/benchmark-report-schema.json in tests/unit/test_quality_evaluator.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - 6개 전체 모델 벤치마크 지표 완전 표출 (Priority: P1) 🎯 MVP

**Goal**: Guarantee all 6 models (Gemma 4 E2B, E4B, 12B & Qwen 3.5 2B, 4B, 9B) are 100% captured and displayed in comparison table with zero omitted rows.

**Independent Test**: Run `python scripts/benchmark_quality.py --auto-download --real` and verify comparison table in generated report contains exactly 6 model rows.

### Tests for User Story 1

- [ ] T004 [P] [US1] Unit test for 6-model report catalog complete rendering in tests/unit/test_quality_evaluator.py

### Implementation for User Story 1

- [ ] T005 [US1] Update run_real_benchmark_loop and exception handler in scripts/benchmark_quality.py to ensure all 6 catalog models are 100% recorded in output report table

**Checkpoint**: User Story 1 fully functional and testable independently (MVP ready!)

---

## Phase 4: User Story 2 - 골든 데이터셋 vs 실제 모델 생성 답변 상세 비교 표출 (Priority: P1)

**Goal**: Render side-by-side text comparisons between Golden Reference Ground Truth and actual generated model responses with error tags and collapsible HTML `<details><summary>` tags.

**Independent Test**: Verify Section 3 of generated report contains collapsible Markdown comparison blocks with ROUGE-L F1 and error tags.

### Tests for User Story 2

- [ ] T006 [P] [US2] Unit test for qualitative sample text diff and error tag extraction in tests/unit/test_quality_evaluator.py

### Implementation for User Story 2

- [ ] T007 [US2] Update QualityEvaluator in src/eval/quality_evaluator.py to extract raw responses, golden ground truth, ROUGE-L F1, Exact Match, JSON validation, and error tags ([JSON Format Failure], [Entity Hallucination], etc.)
- [ ] T008 [US2] Refactor generate_markdown_report in scripts/benchmark_quality.py to render Section 3 with GitHub Markdown <details><summary> collapsible text diff blocks

**Checkpoint**: User Stories 1 and 2 work independently.

---

## Phase 5: User Story 3 - 모델별 컨텍스트 윈도우 크기 한계량 및 스케일링 측정 (Priority: P1)

**Goal**: Benchmark context scaling across `n_ctx` values (4K, 8K, 16K, 32K) and render Peak VRAM and TTFT latency scaling table with VRAM Safety Thresholds.

**Independent Test**: Verify Section 4 of generated report contains context window capacity & scaling limits table across all 6 models.

### Tests for User Story 3

- [ ] T009 [P] [US3] Integration test for context scaling benchmark (n_ctx: 4K, 8K, 16K, 32K) in tests/integration/test_quality_benchmark.py

### Implementation for User Story 3

- [ ] T010 [US3] Implement benchmark_context_scaling in scripts/benchmark_quality.py measuring Peak VRAM and TTFT across n_ctx steps (4096~32768) and render Section 4 Context Window Capacity & Scaling Limits table

**Checkpoint**: User Stories 1, 2, and 3 functional.

---

## Phase 6: User Story 4 - 다중 페르소나 심층 분석 보고서 통합 (Priority: P2)

**Goal**: Synthesize and render 5-persona deep analysis sections (Data Analyst, Deep Learning Expert, Fine-Tuning Expert, DevOps Manager, AI Architect) in report.

**Independent Test**: Verify Section 5 of generated report contains complete 5-persona deep analysis report.

### Tests for User Story 4

- [ ] T011 [P] [US4] Unit test for 5-persona deep analysis section generator in tests/unit/test_quality_evaluator.py

### Implementation for User Story 4

- [ ] T012 [US4] Implement generate_multi_persona_analysis in scripts/benchmark_quality.py synthesizing Data Analyst, DL Expert, Fine-Tuning Expert, DevOps Manager, and AI Architect sections

**Checkpoint**: All user stories functional and complete.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, refactoring, and test suite execution

- [ ] T013 [P] Execute full pytest test suite (74+ tests) in tests/ to verify zero remaining regressions
- [ ] T014 Execute runnable quickstart validation guide in specs/013-enhance-benchmark-report/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS user stories
- **User Stories (Phase 3+)**: Depend on Foundational phase completion
  - Sequential priority order: US1 (P1) → US2 (P2) → US3 (P3) → US4 (P2)
- **Polish (Phase 7)**: Depends on all user stories completion

### Parallel Opportunities

- T003, T004, T006, T009, T011, T013 marked [P] can run in parallel.
