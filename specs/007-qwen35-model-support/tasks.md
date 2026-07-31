# Tasks: Qwen3.5 모델 3종 (2B, 4B, 9B) 서비스 추가 및 성능 검증 (Qwen3.5 Model Support & Benchmarking)

**Input**: Design documents from `/specs/007-qwen35-model-support/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Project root: `/home/dev/storage/vllm_serv/`
- Core modules: `src/core/`
- API routes: `src/api/routes/`
- Scripts: `scripts/`
- Tests: `tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Define data structures and Pydantic schemas for Qwen3.5 presets and benchmark reports

- [x] T001 Define `QwenModelPreset` Pydantic v2 model in `src/core/process_manager.py`
- [x] T002 Define `BenchmarkMetric` and `QwenPerformanceReport` Pydantic v2 models in `scripts/benchmark_qwen35.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Configure Qwen3.5 model paths, VRAM hardware limits, ChatML templates, and Dry-run checks

- [x] T003 Register Qwen3.5 2B, 4B, 9B (Q4_K_M, Q4_0, Q8_0) GGUF paths and ChatML template args (`--chat_template chatml`) (FR-001, FR-009) in `src/core/process_manager.py`
- [x] T004 Add Qwen3.5 hardware VRAM limit lookup dictionary and Dry-run VRAM calculation check (FR-002, FR-010) in `src/core/process_manager.py`

---

## Phase 3: User Story 1 - Qwen3.5 모델 라인업 사전 설정 및 동적 교체 (Priority: P1) 🎯 MVP

**Goal**: Qwen3.5 2B, 4B, 9B 모델 사전 설정 등록 및 대시보드 API를 통한 동적 프로세스 스위칭 연동.

**Independent Test**: `/dashboard/api/capabilities`에서 Qwen3.5 모델 프리셋을 조회하고, `/dashboard/api/apply` 요청 시 Qwen3.5 프로세스가 로드되어 SSE 상태 이벤트가 `READY`로 전환되는지 테스트.

### Implementation for User Story 1

- [x] T005 [P] [US1] Add Qwen3.5 model presets to default configurations in `src/core/config_manager.py`
- [x] T006 [P] [US1] Update `dashboard_api.py` `/capabilities` and `/apply` routes to support Qwen3.5 presets in `src/api/routes/dashboard_api.py`
- [x] T007 [US1] Add unit tests for Qwen3.5 preset selection and ProcessManager ChatML template binding in `tests/unit/test_qwen_manager.py`

**Checkpoint**: User Story 1 complete - Qwen3.5 2B, 4B, 9B models added to presets and switchable via API.

---

## Phase 4: User Story 2 - Qwen3.5 + Gemma 4 교차 성능 측정 및 분석 보고서 생성 (Priority: P1)

**Goal**: Gemma 4 (E2B, E4B, 12B) 재검증 지표 및 Qwen3.5 (2B, 4B, 9B x Q4_K_M, Q4_0, Q8_0) 실측 지표 수집 및 1:1 교차 비교 분석 보고서 자동 생성.

**Independent Test**: `scripts/benchmark_qwen35.py` 실행 시 로딩 시간, TTFT, TPOT, VRAM 피크 수집 후 `specs/007-qwen35-model-support/analysis_report_qwen35.md` 파일 정상 생성 검증.

### Implementation for User Story 2

- [x] T008 [P] [US2] Implement standard prompt dataset generator (Short 100t, Medium 1000t, Long 4000t/8000t) (FR-011) in `scripts/benchmark_qwen35.py`
- [x] T009 [US2] Implement benchmark runner for Gemma 4 (E2B, E4B, 12B) re-verification and Qwen3.5 3-quantization testing (FR-003, FR-007, FR-008) in `scripts/benchmark_qwen35.py`
- [x] T010 [US2] Implement Markdown report generator for `specs/007-qwen35-model-support/analysis_report_qwen35.md` (FR-004) in `scripts/benchmark_qwen35.py`
- [x] T011 [US2] Add integration tests for Qwen3.5 benchmark script in `tests/integration/test_qwen_benchmark.py`

**Checkpoint**: User Story 2 complete - Cross-model benchmark automation & analysis report generation verified.

---

## Phase 5: User Story 3 - Qwen3.5 모델 가용성 및 안전성 예외 처리 (Priority: P2)

**Goal**: 지정된 Qwen3.5 모델 파일 미존재 또는 CUDA OOM 초과 시 안전 에러 응답 및 롤백 수행.

**Independent Test**: 존재하지 않는 모델 식별자나 VRAM 임계치 초과 요청 시 status `ERROR` 반환 검증.

### Implementation for User Story 3

- [x] T012 [US3] Implement missing GGUF file check and CUDA OOM fallback handling (FR-010) in `src/core/process_manager.py`
- [x] T013 [US3] Add unit tests for missing model file and OOM error handling in `tests/unit/test_qwen_manager.py`

**Checkpoint**: User Story 3 complete - Exception and OOM fallback handling verified.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final regression testing and quickstart validation

- [x] T014 [P] Execute full 13+ test regression suite (`uv run pytest`) and verify 100% test pass rate
- [x] T015 Validate end-to-end quickstart scenarios in `specs/007-qwen35-model-support/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on US1 completion
- **User Story 3 (Phase 5)**: Can run in parallel with US2 or after US1
- **Polish (Phase 6)**: Depends on all user stories being complete

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & Phase 2 (Data models, Qwen3.5 GGUF paths, ChatML template args)
2. Complete Phase 3 (User Story 1: Presets & dynamic model switching)
3. **STOP and VALIDATE**: Verify Qwen3.5 2B/4B/9B model switching via API and SSE READY status

### Incremental Delivery

1. Setup + Foundational -> Infrastructure ready
2. User Story 1 -> Qwen3.5 Model Presets & Dynamic Switch (MVP)
3. User Story 2 -> Gemma 4 + Qwen3.5 Cross-Model Benchmark & Analysis Report Generation
4. User Story 3 -> File Missing & OOM Fallback Error Handling
5. Polish -> 100% pytest regression pass
