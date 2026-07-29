# Tasks: GPU VRAM 오프로드 완료 타이밍 보정 및 프로세스 바인딩 격리 (GPU VRAM Offload & Process Lifecycle Timing Fix)

**Input**: Design documents from `/specs/011-fix-vram-offload-timing/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md, contracts/

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

**Purpose**: Define process lifecycle timing models, PyNVML C-API VRAM inspection, and KV Cache VRAM estimator

- [x] T001 Define `ProcessLifecycleState` and `VramLoadTimingGuard` Pydantic models in `src/core/process_manager.py`
- [x] T002 Implement PyNVML (`pynvml`) C-API VRAM inspection helper and GGUF KV Cache pre-flight VRAM estimator ($2 \cdot L \cdot H \cdot D \cdot n_{ctx}$) (FR-008, FR-012) in `src/core/gpu_detector.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement Graceful Stream Drain, sequential process teardown, socket `SO_REUSEADDR` port clearing, and zombie collision guards

- [x] T003 Implement Graceful Stream Drain (`active_requests == 0`, max 5s timeout) and sequential process teardown (SIGTERM -> SIGKILL -> `SO_REUSEADDR` port release check -> PyNVML VRAM baseline check) in `ProcessManager.stop_process()` (FR-002, FR-005, FR-010, FR-011) in `src/core/process_manager.py`
- [x] T004 [P] Implement zombie process and port 8081 collision detector (raising `PortCollisionError`) in `src/core/process_manager.py`

---

## Phase 3: User Story 1 - GPU VRAM 100% 오프로드 완료 기반 READY 상태 전환 (Priority: P1) 🎯 MVP

**Goal**: 서빙 프로세스 개설 시 단순 HTTP 200 응답만으로 조기 READY로 전환되지 않고, stdout 로그 100% VRAM 오프로드 및 네이티브 `/health` JSON API가 동시 확인된 경우에만 READY로 전환되도록 보정하고 K8s readiness API를 노출.

**Independent Test**: 프로세스 개설 시 VRAM 오프로드 완료 전 HTTP 200 OK 판정 조기 전환이 방지되고, `/health` JSON 및 오프로드 완납 후 READY로 전환되는지 단위/통합 테스트로 검증.

### Implementation for User Story 1

- [x] T005 [P] [US1] Write unit tests for PyNVML VRAM inspection, KV Cache estimation, and `/health` JSON API READY synchronization in `tests/unit/test_gpu_detector.py`
- [x] T006 [US1] Update `LlamaManager._wait_for_ready()` to check BOTH `/health` JSON API (`status: "ok"`) AND `vram_offloaded_100pct == True` (polling with `max_retries=10`, `interval=0.5s`, max 5s timeout) before setting state to READY (FR-001, FR-003, FR-009) in `src/core/llama_manager.py`
- [x] T007 [P] [US1] Expose K8s & LiteLLM-compatible `GET /health/liveness` and `GET /health/readiness` endpoints in `src/api/server.py` (FR-013)
- [x] T008 [US1] Block incoming inference requests in `LlamaManager` while process is in `LOADING` status prior to `vram_offloaded_100pct=True` (FR-003) in `src/core/llama_manager.py`

**Checkpoint**: User Story 1 complete - PyNVML VRAM inspection, `/health` API sync, K8s readiness probes, and READY transition verified.

---

## Phase 4: User Story 2 - 기존 프로세스/포트 바인딩 완벽 해제 및 VRAM 동기화 (Priority: P2)

**Goal**: 모델 스위칭 또는 벤치마크 재개설 시 진행 중인 스트림이 안전 종료(Graceful Drain)되고, 이전 프로세스, 포트 소켓(`SO_REUSEADDR`), PyNVML VRAM 점유가 완전 해제된 후 신규 프로세스가 개설되는지 보장.

**Independent Test**: 스위칭 시 이전 PID 종료, 포트 연결 거부 및 PyNVML VRAM 반납이 완료된 후 신규 서빙이 시작되는지 검증.

### Implementation for User Story 2

- [x] T009 [P] [US2] Write integration tests for Graceful Stream Drain, process termination, `SO_REUSEADDR` socket release, and PyNVML VRAM baseline verification in `tests/integration/test_gpu_validation.py`
- [x] T010 [US2] Implement synchronous `_wait_for_port_free()` and `verify_vram_released()` checks (with `max_retries=10`, `interval=0.5s`, max 5s timeout) inside `ProcessManager.spawn_process()` prior to child execution (FR-002, FR-010) in `src/core/process_manager.py`

**Checkpoint**: User Story 2 complete - Process teardown, Graceful Stream Drain, `SO_REUSEADDR` socket isolation, and PyNVML release verified.

---

## Phase 5: User Story 3 - 벤치마크 루프 실측 타이밍 및 평시 서비스 원상 복원 (Priority: P3)

**Goal**: 벤치마크 스크립트 실행 시 각 모델별 `/health` JSON API & VRAM 탑재 완료 대기 및 벤치마크 종료 후 기본 서비스 모델(`qwen3.5-4b`)로 원상 복원 보장.

**Independent Test**: `--auto-download --real` 벤치마크 실행 시 타임아웃 오류 없이 모든 모델의 GPU 실측 추론이 완료되고, 종료 후 `qwen3.5-4b`가 VRAM에 재로드되는지 검증.

### Implementation for User Story 3

- [x] T011 [P] [US3] Update `scripts/benchmark_quality.py` Step 3 to explicitly poll for `/health` JSON API and `vram_offloaded_100pct` in `ProcessManager` status before proceeding to Step 4 inference (FR-004, FR-009) in `scripts/benchmark_quality.py`
- [x] T012 [US3] Add default model residency helper `ensure_default_model_resident()` in `src/core/llama_manager.py` for normal serving startup (FR-006) in `src/core/llama_manager.py`
- [x] T013 [US3] Implement post-benchmark default model restoration (`qwen3.5-4b` re-load into VRAM via `ensure_default_model_resident()`) in `scripts/benchmark_quality.py` (FR-006, FR-007) in `scripts/benchmark_quality.py`

**Checkpoint**: User Story 3 complete - Benchmark timing sync and default resident model restoration verified.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Execute regression test suite and validate quickstart guide scenarios

- [x] T014 Run full regression test suite (`uv run pytest`) and validate scenario steps in `specs/011-fix-vram-offload-timing/quickstart.md`

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

1. Complete Phase 1 & Phase 2 (Pydantic models, PyNVML helper, KV Cache estimator, teardown & drain guards)
2. Complete Phase 3 (User Story 1: PyNVML VRAM inspection, `/health` JSON API, K8s readiness probe & READY state synchronization)
3. **STOP and VALIDATE**: Verify READY state transition timing via pytest

### Incremental Delivery

1. Setup + Foundational -> PyNVML & Teardown Socket Isolation Core Ready
2. User Story 1 -> VRAM 100% Offload Log Sync, `/health` API, K8s Readiness & READY Guard (MVP)
3. User Story 2 -> Process Teardown, Graceful Drain & Socket Port Verification
4. User Story 3 -> Benchmark Timing Sync & Post-Benchmark Default Model Restoration
5. Polish -> Full pytest regression pass & Quickstart scenario validation
