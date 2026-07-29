# Tasks: 자동 모델 다운로드 및 동적 서빙 프로세스 실행 관리 (Automatic Model Download & Dynamic Serving Automation)

**Input**: Design documents from `/specs/009-auto-model-download-serving/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Project root: `/home/dev/storage/vllm_serv/`
- Core modules: `src/core/`
- Evaluation modules: `src/eval/`
- Scripts: `scripts/`
- Tests: `tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Define Pydantic models for model download tasks and process states

- [x] T001 Define `ModelDownloadTask` and `ServerProcessState` Pydantic v2 models in `src/core/model_downloader.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement HuggingFace Hub download engine and dynamic process switching with VRAM cleanup

- [x] T002 Implement HuggingFace Hub GGUF and mmproj CLIP download engine with resume & progress reporting (FR-001, FR-002) in `src/core/model_downloader.py`
- [x] T003 Implement dynamic `llama-server` process switching with SIGTERM/SIGKILL escalation & VRAM cleanup (FR-004) in `src/core/process_manager.py`

---

## Phase 3: User Story 1 - 미존재 GGUF 모델 자동 다운로드 및 검증 (Priority: P1) 🎯 MVP

**Goal**: 로컬 GGUF 파일 미존재 시 HuggingFace Hub에서 자동 다운로드 후 보관 및 검증 구현.

**Independent Test**: 모델 폴더가 비어있는 상태에서 다운로더 구동 시 HuggingFace Hub에서 파일이 자동 다운로드되는지 독립 검증.

### Implementation for User Story 1

- [x] T004 [P] [US1] Implement automatic missing GGUF weight detection and downloader integration (FR-003) in `src/core/model_downloader.py`
- [x] T005 [US1] Add unit tests for HuggingFace model downloader and download task state tracking in `tests/unit/test_model_downloader.py`

**Checkpoint**: User Story 1 complete - Automatic GGUF weight downloader verified.

---

## Phase 4: User Story 2 - llama-server 동적 라이프사이클 관리 및 서빙 자동화 (Priority: P2)

**Goal**: 기존 서빙 프로세스 무중단 종료, VRAM 반납 후 신규 모델 개설 및 HTTP 포트 준비 완료 바인딩.

**Independent Test**: 모델 스위칭 API 구동 시 기존 프로세스 종료, VRAM 해제, `/v1/models` 헬스체크 READY 정상 반환 검증.

### Implementation for User Story 2

- [x] T006 [P] [US2] Implement HTTP health check client (/v1/models polling) and ready state transition in `src/core/llama_manager.py`
- [x] T007 [US2] Add integration tests for dynamic process switching and VRAM release in `tests/integration/test_serving_switch.py`

**Checkpoint**: User Story 2 complete - Dynamic server switching and HTTP health check verified.

---

## Phase 5: User Story 3 - 자동 다운로드 + 로드 + 3D 실측 벤치마크 원스톱 구동 (Priority: P3)

**Goal**: 단 한 번의 벤치마크 명령으로 다운로드-프로세스로딩-GPU실측연동-보고서 생성을 원스톱 수행.

**Independent Test**: `python scripts/benchmark_quality.py --auto-download --real` 구동 시 6개 모델에 대해 원스톱 벤치마크 수행 검증.

### Implementation for User Story 3

- [x] T008 [US3] Integrate one-stop auto-download + real inference server loop (`--auto-download --real`) (FR-005) in `scripts/benchmark_quality.py`

**Checkpoint**: User Story 3 complete - One-stop real GPU inference benchmark automation verified.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final pytest regression suite pass and quickstart scenario validation

- [x] T009 [P] Execute full pytest regression test suite (`uv run pytest`) and verify 100% test pass rate
- [x] T010 Validate end-to-end quickstart scenarios in `specs/009-auto-model-download-serving/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on US1 completion
- **User Story 3 (Phase 5)**: Depends on US1 & US2 completion
- **Polish (Phase 6)**: Depends on all user stories completion

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & Phase 2 (Pydantic models, HuggingFace downloader, process manager switching)
2. Complete Phase 3 (User Story 1: Automatic GGUF downloader & unit tests)
3. **STOP and VALIDATE**: Verify HuggingFace downloader functionality via pytest

### Incremental Delivery

1. Setup + Foundational -> HuggingFace Downloader & Server Switch Core Ready
2. User Story 1 -> Automatic GGUF Model Downloader (MVP)
3. User Story 2 -> Dynamic Server Process Lifecycle & HTTP Health Check
4. User Story 3 -> One-stop Real GPU Inference Benchmark Pipeline
5. Polish -> 100% pytest regression pass

---

## Phase 7: Convergence

- [x] T011 Add `--real-inference` CLI flag support alongside `--real` in `scripts/benchmark_quality.py` per FR-005, US3/AC1 (partial)
- [x] T012 Enhance download progress callback to calculate and report byte-level transfer speed and size per FR-002 (partial)

---

## Phase 8: Convergence

- [x] T013 Fix invalid Qwen HuggingFace repository IDs in `MODEL_DOWNLOAD_CATALOG` (`Qwen/Qwen2.5-*-Instruct-GGUF`) in `src/core/model_downloader.py` per FR-001, US1/AC1 (contradicts)
- [x] T014 Fix `llama-server` process invocation in `src/core/process_manager.py` to support `llama-server` binary or fallback when `llama_cpp.server` module is missing per FR-004, US2/AC1 (contradicts)
- [x] T015 Add empty reports list check guard in `generate_markdown_report` in `scripts/benchmark_quality.py` to prevent `IndexError` when models fail or skip per FR-005 (partial)

---

## Phase 9: Convergence

- [x] T016 Update `MODEL_DOWNLOAD_CATALOG` in `src/core/model_downloader.py` to use valid Qwen 3.5 GGUF repositories (`unsloth/Qwen3.5-2B-GGUF`, `unsloth/Qwen3.5-4B-GGUF`, `unsloth/Qwen3.5-9B-GGUF`) and filenames (`Qwen3.5-2B-Q4_K_M.gguf`, `Qwen3.5-4B-Q4_K_M.gguf`, `Qwen3.5-9B-Q4_K_M.gguf`) per FR-001, US1/AC1 (contradicts)



