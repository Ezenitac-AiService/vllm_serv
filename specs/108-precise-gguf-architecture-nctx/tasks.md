# Tasks: GGUF 모델 메타데이터/카탈로그 파라미터 정밀 추출을 통한 경량 모델 상한선 자동 연산 정밀화 (Precise GGUF Architecture & Uncapped Model Range)

**Input**: Design documents from `/specs/108-precise-gguf-architecture-nctx/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- File paths are explicitly specified in task descriptions.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Environment verification and prerequisite setup

- [X] T001 Verify virtualenv environment (`uv run pytest --version`) and PyNVML driver bindings
- [X] T002 Verify model catalog config and profiles integrity in `config/model_catalog.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure and base utilities for GQA & dynamic step calculations

- [X] T003 Implement GQA KV cache VRAM formula ($\text{KV\_bytes\_per\_token} = 2 \times n_{\text{layers}} \times n_{\text{head\_kv}} \times head\_dim \times \text{bytes\_per\_elem}$) in `src/core/gpu_detector.py`
- [X] T004 Implement log-scaled dynamic step size calculation ($\text{step} = \max(512, 2^{\lfloor \log_2(high / 64) \rfloor})$) in `src/core/gpu_detector.py`
- [X] T005 [P] Create unit tests for GQA VRAM formula and log step size in `tests/unit/test_gpu_detector.py`

---

## Phase 3: User Story 1 - GGUF 메타데이터 및 카탈로그 아키텍처 정밀 파싱 (Priority: P1) 🎯 MVP

**Goal**: GGUF 바이너리 파일 헤더 및 카탈로그 명세로부터 실제 `n_layers`, `n_heads`, `head_dim`, `n_head_kv`를 정밀 파싱하여 2B/4B 경량 모델의 KV 캐시 VRAM 크기(MB/token)를 실측 역산.

**Independent Test**: `uv run pytest tests/unit/test_gpu_detector.py` 및 `test_benchmark_context_window.py` 구동 시 `gemma4-e2b` 11GB VRAM 상한선 역산 결과가 32768 이상으로 정상 계산되는지 검증.

### Tests for User Story 1 (MANDATORY) ⚠️

- [X] T006 [P] [US1] Create unit test for GQA `n_head_kv` reverse calculation (`test_gqa_kv_vram_calculation`) in `tests/unit/test_gpu_detector.py`
- [X] T007 [P] [US1] Create unit test for GGUF binary header parser fallback hierarchy in `tests/unit/test_gpu_detector.py`

### Implementation for User Story 1

- [X] T008 [US1] Implement GGUF binary header metadata extractor (`read_gguf_metadata_architecture`) in `src/core/gpu_detector.py`
- [X] T009 [US1] Update `calculate_max_allocatable_n_ctx` in `src/core/gpu_detector.py` to use `n_head_kv` and dynamic GGUF metadata fallback
- [X] T010 [US1] Update `scripts/benchmark_context_window.py` to fetch exact `n_head_kv` and `max_rope_n_ctx` from model catalog / GGUF metadata

**Checkpoint**: User Story 1 is fully functional and testable independently (`uv run pytest tests/unit/test_gpu_detector.py`).

---

## Phase 4: User Story 2 - 가용 VRAM 여유 상태에서의 이진 탐색 구간 자동 재확장 (Priority: P1) 🎯 MVP

**Goal**: 상한선 `high` 도달 후 테스트 통과(`PASS`) 시 VRAM 사용량이 가용 VRAM의 50% 미만일 경우 `high`를 2배 또는 무제한 모델 RoPE까지 동적 자동 재확장하여 연장 탐색.

**Independent Test**: `uv run python scripts/benchmark_context_window.py --model gemma4-e2b --fine-grained` 구동 시 탐색 구간이 11264에서 멈추지 않고 32768 토큰 또는 OOM 경계선까지 자동 재확장 탐색되는지 검증.

### Tests for User Story 2 (MANDATORY) ⚠️

- [X] T011 [P] [US2] Create unit test for dynamic upper bound re-expansion (`test_dynamic_range_reexpansion`) in `tests/unit/test_benchmark_context_window.py`
- [X] T012 [P] [US2] Create unit test verifying log-scaled dynamic step size in `tests/unit/test_benchmark_context_window.py`

### Implementation for User Story 2

- [X] T013 [US2] Implement range re-expansion algorithm (`high = min(high * 2, model_max_rope)` when `free_vram_ratio >= 0.50`) in `scripts/benchmark_context_window.py`
- [X] T014 [US2] Implement dynamic log step size calculation in binary search loop in `scripts/benchmark_context_window.py`

**Checkpoint**: User Stories 1 AND 2 are both independently functional and testable.

---

## Phase 5: User Story 3 - 카탈로그 명세 내 모델 아키텍처 정밀 파라미터 동기화 (Priority: P2)

**Goal**: `config/model_catalog.json` 내 지원 6개 모델에 대한 `n_layers`, `n_heads`, `head_dim`, `n_head_kv` 정밀 파라미터 사전 동기화.

**Independent Test**: `config/model_catalog.json` 파싱 검증 및 `test_config_manager.py` 실행.

### Tests for User Story 3 (MANDATORY) ⚠️

- [X] T015 [P] [US3] Create unit test verifying architecture parameters for catalog models in `tests/unit/test_config_manager.py`

### Implementation for User Story 3

- [X] T016 [US3] Update `config/model_catalog.json` to include exact `n_layers`, `n_heads`, `head_dim`, `n_head_kv` entries for `gemma4-e2b`, `gemma4-e4b`, `gemma4-12b`, `qwen3.5-2b`, `qwen3.5-4b`, `qwen3.5-9b`

**Checkpoint**: All user stories are independently functional with accurate catalog specifications.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Full regression testing and validation against quickstart scenarios

- [X] T017 Run quickstart validation scenarios from `specs/108-precise-gguf-architecture-nctx/quickstart.md`
- [X] T018 Run complete test suite (`uv run pytest tests/unit/`) across all unit tests
- [X] T019 Verify Constitution Principle II compliance across codebase

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Phase 1 completion.
- **User Story 1 (Phase 3)**: Depends on Phase 2 completion.
- **User Story 2 (Phase 4)**: Depends on Phase 2 completion.
- **User Story 3 (Phase 5)**: Depends on Phase 3 & 4 completion.
- **Polish (Phase 6)**: Depends on all user stories being complete.

---

## Parallel Execution Opportunities

- T005, T006, T007, T011, T012, T015 can be executed in parallel (independent unit test files/methods).

---

## Implementation Strategy (MVP First)

1. **MVP Scope**: Complete Phase 1 ~ Phase 3 (User Story 1 - GQA formula & GGUF header parser).
2. **Increment 2**: Add Phase 4 (User Story 2 - Range re-expansion & log step size).
3. **Increment 3**: Add Phase 5 (User Story 3 - Catalog model architecture params update).
4. **Final Polish**: Run `quickstart.md` scenarios and full `uv run pytest tests/unit/` test suite.
