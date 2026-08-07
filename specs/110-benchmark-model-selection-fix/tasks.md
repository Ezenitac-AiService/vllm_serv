# Tasks: 벤치마크 파이프라인 최적 모델 및 컨텍스트 윈도우 동적 선정 로직 정상화 (Fix Benchmark Model & Context Window Selection Logic)

**Input**: Design documents from `/specs/110-benchmark-model-selection-fix/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- File paths are explicitly specified in task descriptions.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Environment verification and CLI parser structure check

- [x] T001 Verify `scripts/benchmark_context_window.py` CLI parser structure and `--force-benchmark` argument handling

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Safe dictionary key dereferencing helper for schema alignment

- [x] T002 Implement safe metric accessor helper (`get_benchmark_metric`) in `scripts/benchmark_context_window.py` to dereference `tpot_tok_per_sec`, `recommended_context_length`, `max_context_length`, `peak_vram_mb` with fallback fallbacks

---

## Phase 3: User Story 1 - 실측 벤치마크 기반 최적 모델 및 dynamic 컨텍스트 윈도우 동적 반영 (Priority: P1) 🎯 MVP

**Goal**: `evaluate_all_catalog_models`에서 C-B-A 혼합 정렬 알고리즘(1단계: 8K/4K/2K Fallback 파라미터 품질 우대, 2단계: 복합 평가 점수, 3단계: raw n_ctx 및 TPS 내림차순)을 적용하여 이진 탐색으로 실측된 최고 context window 및 최적 서빙 모델이 Stage 4 설정 파일에 100% 동적 반영되도록 교정.

**Independent Test**: `uv run python scripts/benchmark_context_window.py --force-benchmark` 실행 시 Stage 4 결과에 hardcoded `4096` 및 첫 번째 모델 고정 선택 대신 실측 탐색된 dynamic context window(예: 16384, 20480) 및 C-B-A 최고 모델이 정확히 표시되고 저장됨을 확인.

### Tests for User Story 1 (MANDATORY) ⚠️

- [x] T003 [P] [US1] Create unit test for dynamic context window selection and C-B-A hybrid sorting algorithm (`test_evaluate_all_catalog_models_cba_sorting`) in `tests/unit/test_benchmark_context.py`

### Implementation for User Story 1

- [x] T004 [US1] Implement C-B-A hybrid model score calculator and 8K -> 4K -> 2K graceful fallback algorithm in `scripts/benchmark_context_window.py`
- [x] T005 [US1] Update `evaluate_all_catalog_models` in `scripts/benchmark_context_window.py` to use safe metric dereferencing and C-B-A hybrid sorting
- [x] T006 [US1] Update Stage 4 logger and `save_benchmark_profile` call in `scripts/benchmark_context_window.py` to persist `recommended_context_length` dynamically instead of hardcoded 4096

**Checkpoint**: User Story 1 is fully functional and testable independently (`uv run python scripts/benchmark_context_window.py --force-benchmark`).

---

## Phase 4: User Story 2 - 딕셔너리 키 불일치 및 Fallback 하드코딩 결함 교정 (Priority: P2)

**Goal**: 벤치마크 모듈 간 반환 딕셔너리 스키마(`tpot_tok_per_sec`, `max_context_length`, `recommended_context_length`, `peak_vram_mb`)를 단일화하고 단위 테스트 수트 강화.

**Independent Test**: `uv run pytest tests/unit/test_benchmark_context.py` 실행 시 모든 키 참조 및 스키마 검증 테스트가 100% Green 통과.

### Tests for User Story 2 (MANDATORY) ⚠️

- [x] T007 [P] [US2] Add unit test for schema key dereferencing consistency across fine-grained binary search and partial cache miss (`test_benchmark_result_schema_consistency`) in `tests/unit/test_benchmark_context.py`

### Implementation for User Story 2

- [x] T008 [US2] Update `sync_partial_cache_miss` and `_record_unsupported_fallback_profile` in `scripts/benchmark_context_window.py` to use unified schema key accessors

**Checkpoint**: User Stories 1 AND 2 are both independently functional.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Quickstart validation and full test suite verification

- [x] T009 Run quickstart validation scenarios from `specs/110-benchmark-model-selection-fix/quickstart.md`
- [x] T010 Run complete unit test suite (`uv run pytest tests/unit/`) across all unit tests
- [x] T011 Verify Constitution Principle II & DoD compliance

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Phase 1 completion.
- **User Story 1 (Phase 3)**: Depends on Phase 2 completion.
- **User Story 2 (Phase 4)**: Depends on Phase 2 completion.
- **Polish (Phase 5)**: Depends on all user stories being complete.

---

## Implementation Strategy (MVP First)

1. **MVP Scope**: Complete Phase 1 ~ Phase 3 (User Story 1 - Dynamic context window & C-B-A model selection).
2. **Increment 2**: Add Phase 4 (User Story 2 - Schema unification & partial cache miss key consistency).
3. **Final Polish**: Run `quickstart.md` scenarios and full `uv run pytest tests/unit/` test suite.

