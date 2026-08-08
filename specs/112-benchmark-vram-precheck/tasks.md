# Tasks: 벤치마크 품질 평가 스크립트 VRAM 용량 사전 검증 및 자동 스킵 (Benchmark VRAM Pre-check & Auto-Skip)

**Input**: Design documents from `/specs/112-benchmark-vram-precheck/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- File paths are explicitly specified in task descriptions.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify core VRAM estimation helpers and GPU detector interfaces

- [x] T001 Verify VRAM estimation helper entrypoints (`estimate_vram_requirement`) in `src/core/process_manager.py` and GPU memory detector (`get_gpu_memory`) in `src/core/gpu_detector.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core VRAM feasibility check helper bridging downloader and benchmark scripts

- [x] T002 Implement core `check_vram_feasibility` helper function in `src/core/model_downloader.py` connecting `ProcessManager` estimation formula and `GPUDetector` hardware limits

---

## Phase 3: User Story 1 - 모델 다운로드 및 서빙 전 VRAM 용량 사전 검증 및 자동 스킵 (Priority: P1) 🎯 MVP

**Goal**: `model_downloader.py` 및 `benchmark_quality.py`가 GGUF 가중치 원격 다운로드 및 로컬 서빙 개설 전 VRAM 요구량을 사전 산출하여 VRAM 용량 초과 모델(26B/27B 등)을 사전 스킵 (`[SKIP VRAM OOM Risk]`).

**Independent Test**: 11GB VRAM GPU 환경에서 26B/27B 대형 모델 서빙/다운로드 시도 시 16GB+ 다운로드나 서빙 개설을 시도하지 않고 사전 스킵 로그 출력 후 즉시 다음 모델로 진행됨을 실측 검증.

### Tests for User Story 1 (MANDATORY) ⚠️

- [x] T003 [P] [US1] Create unit tests for `check_vram_feasibility` pre-check and auto-skip logic (`test_model_downloader_vram_precheck_skip`) in `tests/unit/test_model_downloader.py`
- [x] T004 [P] [US1] Create unit tests for pre-serve VRAM skip check for local model files (`test_benchmark_vram_precheck_local_file_skip`) in `tests/unit/test_benchmark_context.py`

### Implementation for User Story 1

- [x] T005 [US1] Implement pre-download VRAM feasibility check and skip handler (`check_vram_feasibility`) in `src/core/model_downloader.py` (FR-001, FR-002)
- [x] T006 [US1] Implement pre-serve VRAM feasibility check and skip handler for local files in `scripts/benchmark_quality.py` (FR-006)

**Checkpoint**: User Story 1 is fully functional and testable independently (`uv run python scripts/benchmark_quality.py --auto-download`).

---

## Phase 4: User Story 2 - 벤치마크 구동 시 전수 모델 VRAM 적합성 사전 요약 리포트 (Priority: P2)

**Goal**: `benchmark_quality.py` 실행 시작 시 전체 평가 대상 모델 14종의 VRAM 수용 적합성 요약표(`[VRAM SUMMARY]`) 출력.

**Independent Test**: `benchmark_quality.py` 구동 직후 초기 로그에 GPU 스펙 및 모델별 Pass/Skip 요약 테이블이 정상 출력됨을 확인.

### Tests for User Story 2 (MANDATORY) ⚠️

- [x] T007 [P] [US2] Create unit tests for benchmark VRAM summary table generation (`test_benchmark_vram_summary_report`) in `tests/unit/test_benchmark_context.py`

### Implementation for User Story 2

- [x] T008 [US2] Implement benchmark full catalog VRAM evaluation summary report (`print_vram_summary_report`) in `scripts/benchmark_quality.py` (FR-003)

**Checkpoint**: User Stories 1 AND 2 are both independently functional.

---

## Phase 5: User Story 3 - CLI 실행 옵션으로 VRAM 사전 검증 강제 제어 (Priority: P3)

**Goal**: `--ignore-vram-check` CLI 옵션 지원으로 VRAM 검증 및 자동 스킵 동작 우회.

**Independent Test**: `benchmark_quality.py --auto-download --ignore-vram-check` 실행 시 VRAM 초과 경고만 출력하고 다운로드/서빙을 강제 수행함을 확인.

### Tests for User Story 3 (MANDATORY) ⚠️

- [x] T009 [P] [US3] Create unit tests for `--ignore-vram-check` CLI flag handling in `tests/unit/test_model_downloader.py`

### Implementation for User Story 3

- [x] T010 [US3] Implement `--ignore-vram-check` argument parsing and bypass condition in `src/core/model_downloader.py` and `scripts/benchmark_quality.py` (FR-004)

**Checkpoint**: All User Stories (US1, US2, US3) are fully functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Quickstart validation and full test suite verification

- [x] T011 Run quickstart validation scenarios from `specs/112-benchmark-vram-precheck/quickstart.md`
- [x] T012 Run full unit test suite (`uv run pytest tests/unit/`) across all unit tests
- [x] T013 Verify Constitution Principle II & DoD compliance

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Phase 1 completion.
- **User Story 1 (Phase 3)**: Depends on Phase 2 completion.
- **User Story 2 (Phase 4)**: Depends on Phase 2 completion.
- **User Story 3 (Phase 5)**: Depends on Phase 3 and 4 completion.
- **Polish (Phase 6)**: Depends on all user stories being complete.

---

## Implementation Strategy (MVP First)

1. **MVP Scope**: Complete Phase 1 ~ Phase 3 (User Story 1 - Pre-download & pre-serve VRAM check & auto-skip).
2. **Increment 2**: Add Phase 4 (User Story 2 - Full benchmark catalog VRAM summary report).
3. **Increment 3**: Add Phase 5 (User Story 3 - `--ignore-vram-check` CLI bypass flag).
4. **Final Polish**: Run `quickstart.md` scenarios and full `uv run pytest tests/unit/` test suite.
