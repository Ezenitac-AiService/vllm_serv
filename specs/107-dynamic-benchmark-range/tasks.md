# Tasks: 동적 모델-KV 메모리 기반 벤치마크 탐색 구간 자동 산정 및 하드코딩 수치 전면 제거 (Dynamic Benchmark Range & Zero Magic Numbers)

**Input**: Design documents from `/specs/107-dynamic-benchmark-range/`

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

**Purpose**: Core infrastructure and base utilities for dynamic VRAM calculation & process management

- [X] T003 Implement dynamic Scratchpad safety margin calculation ($\text{safety\_margin\_mb} = 500 + \lfloor n_{\text{ctx}} \times 0.05 \rfloor$) in `src/core/gpu_detector.py`
- [X] T004 Implement NVML Settling Loop (0.2s interval polling until Delta < 10MB across consecutive reads) in `src/core/gpu_detector.py`
- [X] T005 [P] Create unit test for NVML Settling Loop in `tests/unit/test_gpu_detector.py`

---

## Phase 3: User Story 1 - 실측 GPU VRAM과 모델 아키텍처 한계에 의한 100% 동적 이진 탐색 구간 생성 (Priority: P1) 🎯 MVP

**Goal**: GPU NVML 가용 용량과 모델 카탈로그/GGUF max_n_ctx로부터 하드코딩 캡핑(`16384`, `4096`) 없는 동적 이진 탐색 상한선(`high`) 및 구간을 연산.

**Independent Test**: `uv run pytest tests/unit/test_benchmark_context_window.py` 실행 시 `gemma4-e2b` 11GB VRAM 환경 상한선이 [4096, 16384]로 자동 확장 연산되는지 검증.

### Tests for User Story 1 (MANDATORY) ⚠️

- [X] T006 [P] [US1] Create unit test for dynamic high-bound calculation (`test_dynamic_high_bound_calculation`) in `tests/unit/test_benchmark_context_window.py`
- [X] T007 [P] [US1] Create unit test for small model (`gemma4-e2b`) context range expansion in `tests/unit/test_benchmark_context_window.py`

### Implementation for User Story 1

- [X] T008 [US1] Implement `calculate_max_allocatable_n_ctx` using `estimate_kv_cache_vram` reverse mapping in `src/core/gpu_detector.py`
- [X] T009 [US1] Remove hardcoded upper bound `16384` and `4096` in `scripts/benchmark_context_window.py` and replace with `high = min(model_max_n_ctx, max_allocatable_n_ctx)`
- [X] T010 [US1] Implement dynamic inference timeout scaling ($\text{timeout\_s} = \max(60.0, 30.0 + n_{\text{ctx}} \times 0.005)$) in `scripts/benchmark_context_window.py`

**Checkpoint**: User Story 1 is fully functional and testable independently (`uv run pytest tests/unit/test_benchmark_context_window.py`).

---

## Phase 4: User Story 2 - `stop_server.sh` 및 프로세스 정리에 의한 100% VRAM 해제 보장 (Priority: P2)

**Goal**: Python `llama_cpp.server` 및 백엔드 포트(8089, 8090, 8091) 프로세스를 핀포인트 강제 사살하여 VRAM 100% 완전 해제.

**Independent Test**: Python `llama_cpp.server` 프로세스 구동 후 `./stop_server.sh` 실행 시 잔여 프로세스 0건 및 NVML VRAM 사용량 < 500MB 단정 검증.

### Tests for User Story 2 (MANDATORY) ⚠️

- [X] T011 [P] [US2] Create unit test for `llama_cpp.server` and port 8089/8090/8091 fuser cleanup in `tests/unit/test_process_manager_cleanup.py`
- [X] T012 [P] [US2] Create unit test for TCP TIME_WAIT port readiness check in `tests/unit/test_process_manager_cleanup.py`

### Implementation for User Story 2

- [X] T013 [US2] Add `pgrep -f "llama_cpp.server"` and `fuser -k -9 8089/tcp 8090/tcp 8091/tcp` cleanup commands to `stop_server.sh`
- [X] T014 [US2] Add Python `llama_cpp.server` module patterns and socket port cleanup to `force_kill_zombie_llama_servers` in `src/core/process_manager.py`
- [X] T015 [US2] Add TCP Port Readiness Polling (verify `socket.connect_ex` returns non-zero) to `src/core/process_manager.py`

**Checkpoint**: User Stories 1 AND 2 are both independently functional and testable.

---

## Phase 5: User Story 3 - 하드코딩 매직 넘버 전면 제거 및 실측 척도 100% 반영 (Priority: P3)

**Goal**: 스크립트 및 모듈 내 `remaining_kv_budget < 3000`, `tps_val = 45.0`, `file_size_mb = 3000.0` 상수를 100% 철폐하고 실측값으로 대체.

**Independent Test**: 벤치마크 프로파일 생성 시 실측 TPS (`completion_tokens / elapsed_seconds`) 및 카탈로그 `size_gb` 데이터 반영 검증.

### Tests for User Story 3 (MANDATORY) ⚠️

- [X] T016 [P] [US3] Create unit test verifying zero magic numbers (`remaining_kv_budget < 3000`, `45.0 TPS`) in `tests/unit/test_benchmark_context_window.py`
- [X] T017 [P] [US3] Create unit test for real TPS calculation in `tests/unit/test_benchmark_context_window.py`

### Implementation for User Story 3

- [X] T018 [US3] Remove hardcoded `remaining_kv_budget < 3000` rule in `scripts/benchmark_context_window.py`
- [X] T019 [US3] Remove hardcoded `tps_val = 45.0` fallback in `scripts/benchmark_context_window.py` and replace with real measured TPS (`max_tokens / elapsed_time`)
- [X] T020 [US3] Remove hardcoded `file_size_mb = 3000.0` fallback in `scripts/benchmark_context_window.py` and replace with catalog `size_gb * 1024`

**Checkpoint**: All user stories are independently functional with zero magic numbers.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Full regression testing and validation against quickstart scenarios

- [X] T021 Run quickstart validation scenarios from `specs/107-dynamic-benchmark-range/quickstart.md`
- [X] T022 Run complete test suite (`uv run pytest`) across all unit tests
- [X] T023 Verify Constitution Principle II compliance across codebase

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

- T005, T006, T007, T011, T012, T016, T017 can be executed in parallel (independent unit test files/methods).

---

## Implementation Strategy (MVP First)

1. **MVP Scope**: Complete Phase 1 ~ Phase 3 (User Story 1 - Dynamic upper bound range calculation).
2. **Increment 2**: Add Phase 4 (User Story 2 - `stop_server.sh` VRAM cleanup & socket readiness).
3. **Increment 3**: Add Phase 5 (User Story 3 - Full magic numbers purge & real TPS calculation).
4. **Final Polish**: Run `quickstart.md` scenarios and full `uv run pytest` test suite.
