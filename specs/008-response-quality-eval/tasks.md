# Tasks: 모델 답변 품질 비교 분석 및 자동 검증 테스트 구현 (Response Quality Evaluation & Benchmark)

**Input**: Design documents from `/specs/008-response-quality-eval/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Project root: `/home/dev/storage/vllm_serv/`
- Evaluation modules: `src/eval/`
- Core modules: `src/core/`
- Scripts: `scripts/`
- Tests: `tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Define Pydantic v2 schemas and JSON Schema contract files for quality metrics and benchmark reports

- [x] T001 Define `QualityBenchmarkPrompt`, `QualityEvaluationMetric`, and `ComprehensiveQualityReportMetric` Pydantic v2 models in `src/eval/quality_evaluator.py`
- [x] T002 Create JSON Schema contract definition for structured response validation in `specs/008-response-quality-eval/contracts/quality-eval-schema.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build weighted scoring engine core and load reference benchmark datasets (`ATEAM` & `BTEAM`)

- [x] T003 Implement 60% quantitative + 40% qualitative weighted scoring engine (`Quality Score = 0.6 * Quant + 0.4 * Qual`) (FR-002) in `src/eval/quality_evaluator.py`
- [x] T004 Implement Golden Reference Dataset loader from `src/eval/golden_dataset.json` (Antigravity Gemini 3.6 Flash Teacher LLM draft + Human expert verified ground-truth) for `ATEAM` & `BTEAM` benchmark tasks (FR-001, FR-008) in `src/eval/quality_evaluator.py`

---

## Phase 3: User Story 1 - 다축 기준 기반 모델 답변 품질 자동 평가 엔진 (Priority: P1) 🎯 MVP

**Goal**: Pydantic/JSON 스키마 정합성 검증, 대상/화자 슬롯 추출 정확도(Slot Precision) 산출 및 정제문(`refined_sentence`) 완성도 평가 구현.

**Independent Test**: `QualityEvaluator`를 구동하여 `ATEAM` 및 `BTEAM` 기준 프롬프트에 대해 정량/정성 가중 품질 점수(1.0~5.0)가 정밀 계산되는지 검증.

### Implementation for User Story 1

- [x] T005 [P] [US1] Implement JSON/Markdown format validator & slot extraction precision calculator (FR-002, FR-007) in `src/eval/quality_evaluator.py`
- [x] T006 [P] [US1] Implement ATEAM/BTEAM reference workload evaluator for target/speaker extraction & refined_sentence completeness in `src/eval/quality_evaluator.py`
- [x] T007 [US1] Add unit tests for quality evaluation engine and weighted scoring formula in `tests/unit/test_quality_evaluator.py`

**Checkpoint**: User Story 1 complete - Multi-axis quality evaluation engine and slot precision scoring verified.

---

## Phase 4: User Story 2 - Qwen 3.5 vs Gemma 4 종합 속도-메모리-품질 교차 비교 보고서 생성 (Priority: P2)

**Goal**: 속도(TPOT), 메모리(VRAM), 품질 점수 결합 3D 가성비 지수(`Quality-per-Speed Index`, `Quality-per-VRAM Index`) 산출 및 마크다운 비교 보고서 자동 생성.

**Independent Test**: `scripts/benchmark_quality.py` 실행 시 3D 지표 수집 후 `specs/008-response-quality-eval/analysis_report_quality.md` 정상 생성 검증.

### Implementation for User Story 2

- [x] T008 [P] [US2] Implement 3D efficiency index calculator (Quality-per-Speed Index & Quality-per-VRAM Index) (FR-004) in `scripts/benchmark_quality.py`
- [x] T009 [US2] Implement 3D markdown report generator for `specs/008-response-quality-eval/analysis_report_quality.md` (FR-005) in `scripts/benchmark_quality.py`
- [x] T010 [US2] Add integration tests for 3D quality benchmark runner and report generation in `tests/integration/test_quality_benchmark.py`

**Checkpoint**: User Story 2 complete - 3D quality-speed-VRAM cross-model benchmark automation & report generation verified.

---

## Phase 5: User Story 3 - 환각(Hallucination) 및 지시 탈선 예외 감지 검증 (Priority: P3)

**Goal**: 거짓 정보 작성, 빈 응답, 포맷 파싱 실패 시 자동 감점 및 에러 플래그 설정.

**Independent Test**: 모순되거나 사실 확인이 필요한 프롬프트 요청 시 `error_flags` 수집 및 점수 감점 검증.

### Implementation for User Story 3

- [x] T011 [US3] Implement hallucination detection, empty response handling, and error flagging rules (FR-003) in `src/eval/quality_evaluator.py`
- [x] T012 [US3] Add unit tests for hallucination detection and error flag handling in `tests/unit/test_quality_evaluator.py`

**Checkpoint**: User Story 3 complete - Hallucination detection & error fallback handling verified.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final pytest regression suite pass and quickstart scenario validation

- [x] T013 [P] Execute full pytest regression suite (`uv run pytest`) and verify 100% test pass rate
- [x] T014 Validate end-to-end quickstart scenarios in `specs/008-response-quality-eval/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on US1 completion
- **User Story 3 (Phase 5)**: Can run after US1 completion
- **Polish (Phase 6)**: Depends on all user stories completion

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & Phase 2 (Pydantic models, weighted scoring formula, ATEAM/BTEAM dataset loader)
2. Complete Phase 3 (User Story 1: Quality evaluation engine & slot precision calculator)
3. **STOP and VALIDATE**: Verify Quality Score calculation and slot precision scoring via pytest

### Incremental Delivery

1. Setup + Foundational -> Quality Evaluation Core Ready
2. User Story 1 -> Multi-axis Quality Evaluation Engine (MVP)
3. User Story 2 -> Qwen 3.5 vs Gemma 4 3D Quality-Speed-VRAM Cross Benchmark Report
4. User Story 3 -> Hallucination Detection & Exception Error Flagging
5. Polish -> 100% pytest regression pass
