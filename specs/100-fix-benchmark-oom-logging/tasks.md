# Tasks: 벤치마크 OOM 진단 및 실시간 로그 영구 저장 개선 (100-fix-benchmark-oom-logging)

**Input**: Design documents from `/specs/100-fix-benchmark-oom-logging/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/benchmark-cli-contract.md`, `quickstart.md`

**Organization**: Tasks are grouped by user story (P1 -> P2 -> P3 -> P4) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to ([US1], [US2], [US3], [US4])
- Include exact file paths, class/function names, parameter signatures, and explicit assertions in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Logging directory initialization and permissions setup

- [x] T001 Verify `logs/` directory creation and ensure append write permissions for `logs/benchmark.log` and `logs/error.log` in `scripts/setup.sh`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Unit test harnesses for logging, dynamic VRAM calculation, and profile persistence

- [x] T002 Create unit test harness `TestProcessManagerLogging` in `tests/unit/test_process_manager_logging.py` importing `ProcessManager` and `asyncio` stream mocks
- [x] T003 [P] Create unit test harness `TestDynamicVramCalculation` in `tests/unit/test_dynamic_vram_calculation.py` importing `get_nvml_vram_info` and `estimate_kv_cache_vram`

---

## Phase 3: User Story 1 - 벤치마크 서브프로세스 실시간 로그 영구 저장 및 추적성 확보 (Priority: P1) 🎯 MVP

**Goal**: 백엔드 서브프로세스(`llama-server`)의 stdout/stderr를 `logs/benchmark.log`에 실시간 파일 플러시 스트리밍하고, 비정상 종료/타임아웃 시 최근 20줄 콘솔 덤프를 `logs/error.log`에 보존.

**Independent Test**: `./setup.sh --force-benchmark` 구동 시 `logs/benchmark.log`에 백엔드 실시간 출력이 기록되고 비정상 종료 시 `logs/error.log`에 덤프가 남는지 확인.

### Implementation & Tests for User Story 1

- [x] T004 [P] [US1] Write unit test `test_drain_stdout_flushes_to_log_file()` in `tests/unit/test_process_manager_logging.py` asserting `StreamReader` output is immediately written and `flush()`ed to `logs/benchmark.log`
- [x] T005 [US1] Open `logs/benchmark.log` in append mode within `_drain_stdout(self, stream: asyncio.StreamReader)` in `src/core/process_manager.py` and call `log_file.flush()` after every `stream.readline()` iteration
- [x] T006 [US1] Implement circular buffer `recent_lines = collections.deque(maxlen=50)` inside `_drain_stdout()` in `src/core/process_manager.py` to capture recent subprocess logs
- [x] T007 [US1] Write crash/timeout dump logic inside `_drain_stdout()` in `src/core/process_manager.py` to write the last 20 lines from `recent_lines` to `logs/error.log` and `logs/benchmark.log` when `self.process.returncode != 0` (including explicit Exit Code 137 / SIGKILL Kernel OOM Killer header insertion)
- [x] T008 [US1] Refactor `stop_process()` in `src/core/process_manager.py` to feed EOF to pipe transport and await `_log_drain_task` completion with a 2.0s timeout before calling task cancellation, preventing log loss on process termination
- [x] T009 [US1] Verify US1 log streaming, real-time flushing, and error tail dumping with `uv run pytest tests/unit/test_process_manager_logging.py`

**Checkpoint**: User Story 1 complete - all backend stdout/stderr outputs are written to `logs/benchmark.log` in real time with crash dumps saved to `logs/error.log`.

---

## Phase 4: User Story 2 - 동적 데이터 기반 VRAM 산정식, 500MB 안전 버퍼 및 헬스체크 타임아웃 최적화 (Priority: P2)

**Goal**: 하드코딩된 `"2b"` 검사, VRAM 12000/8000 정적 테이블, `2600+0.4*mid` 가짜 수식, 6000MB 정적 기본값을 완전 제거하고 GGUF 파일 용량 + 500MB 안전 버퍼 감안 NVML 가용 VRAM 기반 동적 KV 예산 계산 및 최대 30초 동적 헬스체크 타임아웃 적용.

**Independent Test**: `uv run python scripts/benchmark_context_window.py --fine-grained --model qwen3.5-4b` 실행 시 10초 타임아웃 오탐 없이 정상 TPS 및 n_ctx 측정.

### Implementation & Tests for User Story 2

- [x] T010 [P] [US2] Write unit tests `test_dynamic_vram_estimation()` and `test_dynamic_polling_timeout()` in `tests/unit/test_dynamic_vram_calculation.py`
- [x] T011 [US2] Implement Base VRAM calculation formula (`os.path.getsize(model_path) * 1.15 / (1024*1024)`) in `spawn_process()` within `src/core/process_manager.py` replacing `base_vram = 6000`
- [x] T012 [US2] Calculate `usable_vram = available_nvml_vram - 500` (500MB Safety Cushion) and `remaining_kv_budget = usable_vram - base_vram` in `_execute_single_binary_search_inner()` in `scripts/benchmark_context_window.py` and set initial `low=2048`, `high=4096` when budget < 3000MB to prevent pre-flight OOM risk blocks
- [x] T013 [US2] Remove `"2b"` model string check and static VRAM tables (`total_vram >= 12000` / `8000`) in `_execute_single_binary_search_inner()` within `scripts/benchmark_context_window.py`
- [x] T014 [US2] Replace static fallback formula `2600 + int(mid * 0.4)` with real NVML VRAM snapshot delta measurement (`gpu_snap.total_vram_mb - gpu_snap.free_vram_mb`) in `scripts/benchmark_context_window.py`
- [x] T015 [US2] Implement dynamic health check polling timeout formula `min(30.0, max(15.0, 10.0 + file_size_mb/500))` in `poll_server_health()` in `src/core/process_manager.py` and call site in `scripts/benchmark_context_window.py`
- [x] T016 [US2] Verify US2 dynamic VRAM estimation and timeout scaling with `uv run pytest tests/unit/test_dynamic_vram_calculation.py`

**Checkpoint**: User Story 2 complete - 100% data-driven dynamic VRAM estimation with 500MB safety cushion and dynamic timeout scaling without hardcoded strings or false OOM risk.

---

## Phase 5: User Story 3 - 벤치마크 결과 프로필 저장, 커널 OOM 진단, 카탈로그 동기화(FR-012) 및 정밀 실패 사유 피드백 (Priority: P3)

**Goal**: `config/model_context_profiles.json` 프로필에 정밀 `failure_reason` (Exit Code 137 Kernel OOM 포함) 수록, `ensure_models.py` / `ModelDownloader`에서 가중치 다운로드 완납 시점 및 기존 파일 존재(Smart Skip) 시점 모두 `config/model_catalog.json` 실측 메타데이터(`exact_bytes`, `size_gb`) 원자적 동기화(`FR-012`), 및 `setup.sh` 내 하드코딩된 모델 배열(`REQUIRED_MODELS`)과 레거시 문자열(`"legacy-i7-930"`) 전면 정제.

**Independent Test**: `./setup.sh --force-benchmark` 완결 후 `config/model_context_profiles.json`에 구체적 failure_reason 및 최적 서빙 모델이 정상 업데이트되고 `config/model_catalog.json`의 실측 파일 크기가 스마트스킵 시에도 반영됨을 검증.

### Implementation & Tests for User Story 3

- [x] T017 [P] [US3] Write unit test `test_failure_reason_json_persistence()` in `tests/unit/test_model_profiles_persistence.py` asserting `failure_reason` string field (including "KERNEL_OOM_KILLER_EXIT_137") is saved in `model_context_profiles.json`
- [x] T018 [US3] Refactor `ensure_models.py` and `src/core/model_downloader.py` to dynamically query required model IDs from `config/server_config.json` (`model`, `embedding_model`, `rerank_model`) and `config/model_catalog.json` instead of hardcoded `REQUIRED_MODELS` list, and implement atomic catalog write-back reconciliation of `exact_bytes` and `size_gb` upon download completion OR Smart Skip local file verification (`FR-012`)
- [x] T019 [US3] Refactor `scripts/setup.sh` to dynamically search for wheel files under `wheels/${MATCHED_PROFILE}/` based on `$MATCHED_PROFILE` variable instead of `"legacy-i7-930"` string match
- [x] T020 [US3] Implement detailed `failure_reason` string recording (`KERNEL_OOM_KILLER_EXIT_137`, `HEALTH_CHECK_TIMEOUT`, `CUDA_OOM_EXCEEDED`, `PROCESS_CRASH_EXIT_<CODE>`, `MODEL_FILE_NOT_FOUND`) in `_record_unsupported_fallback_profile()` in `scripts/benchmark_context_window.py`
- [x] T021 [US3] Verify US3 profile persistence, dynamic catalog provisioning, and Smart Skip catalog metadata write-back reconciliation with `uv run pytest tests/unit/test_model_profiles_persistence.py`

**Checkpoint**: User Story 3 complete - detailed failure_reason recorded in JSON profile, model catalog updated with exact downloaded/local bytes on Smart Skip, and all 5 hardcoded areas cleaned up.

---

## Phase 6: User Story 4 - 벤치마크 로그 파일 로테이션 및 디스크 안정성 보장 (Priority: P4)

**Goal**: `logs/benchmark.log` 파일이 10MB를 초과할 경우 `logs/benchmark.log.old`로 원자적 로테이션하여 디스크 고갈을 방지.

**Independent Test**: `logs/benchmark.log` 10MB 초과 시 로테이션 수행 검증.

### Implementation & Tests for User Story 4

- [x] T022 [P] [US4] Write unit test `test_benchmark_log_rotation()` in `tests/unit/test_process_manager_logging.py` asserting log files > 10MB are rotated to `.old`
- [x] T023 [US4] Implement 10MB log rotation check before opening `logs/benchmark.log` in `_drain_stdout()` in `src/core/process_manager.py` and `scripts/setup.sh`

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: System-wide regression verification and quickstart validation

- [x] T024 Run full suite regression tests via `uv run pytest`
- [x] T025 Execute end-to-end quickstart validation scenarios in `specs/100-fix-benchmark-oom-logging/quickstart.md` via `./setup.sh --force-benchmark`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - starts immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: Depend on Foundational phase completion
  - US1 (P1, MVP) -> US2 (P2) -> US3 (P3) -> US4 (P4)
- **Polish (Phase 7)**: Depends on completion of US1, US2, US3, and US4

### Parallel Opportunities

- T003, T004, T010, T017, T022 (test files across different modules) can run in parallel.
- US1 (T004~T009) completes independently as MVP.
