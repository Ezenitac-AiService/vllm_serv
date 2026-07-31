# Tasks: Fast-Track 휠 검증 서브쉘 종료 코드 캡처 구문 수정 및 C++ 소스 재컴파일 Fallback 정상 전이 보장 (056-fix-subshell-status-code-fallback)

**Input**: Design documents from `/specs/056-fix-subshell-status-code-fallback/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Includes exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initial analysis and script structure verification

- [X] T001 Inspect `scripts/setup.sh` subshell assignments (lines 218, 267) and `src/core/cpu_detector.py` preflight check
- [X] T002 [P] Verify `contracts/fallback-pipeline-api.json` schema requirements

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core script CLI option & environment helper infrastructure

- [X] T003 Ensure `scripts/verify_wheel_binary.py` support for live environment CUDA verification

---

## Phase 3: User Story 1 - Fast-Track 휠 검증 서브쉘 종료 코드 캡처 및 C++ 소스 컴파일 Fallback (Priority: P1) 🎯 MVP

**Goal**: `setup.sh` 내 사전 빌드 휠 GPU 검증 서브쉘 할당 구문을 `GPU_CHECK_OUTPUT=$(uv run python -c "..." 2>&1) || GPU_CHECK_STATUS=$?` 형태로 수정하여 exit code 2 캡처를 보장하고, 오프로드 실패 시 `uv pip uninstall llama-cpp-python` 정리 후 C++ 소스 재컴파일로 100% 전이

**Independent Test**: Fast-Track 휠 GPU 검증이 exit code 2를 반환할 때 스크립트 중단 없이 `[FAST-TRACK FAIL]` 경고 후 `uv pip uninstall` 및 C++ 소스 컴파일 파이프라인으로 전이되는지 단위 테스트로 검증

### Tests for User Story 1
- [X] T004 [P] [US1] Write unit test `test_setup_subshell_error_guard_and_fallback()` in `tests/unit/test_seed_pack.py`

### Implementation for User Story 1
- [X] T005 [US1] Update subshell exit code capture syntax `GPU_CHECK_OUTPUT=$(...) || GPU_CHECK_STATUS=$?` in `scripts/setup.sh`
- [X] T006 [US1] Add `uv pip uninstall llama-cpp-python` clean step before Tier 4 C++ source compilation in `scripts/setup.sh`
- [X] T007 [US1] Verify T004 unit test passes green in `tests/unit/test_seed_pack.py`

**Checkpoint**: User Story 1 complete - Fast-Track subshell exit code 2 accurately captured & Fallback clean step operational

---

## Phase 4: User Story 2 - start_server.sh 2중 사전 점검(Pre-flight) 및 status_server.sh 실측 연동 (Priority: P1) 🎯 MVP

**Goal**: `src/core/cpu_detector.py`의 `check_hardware_preflight()` 및 `start_server.sh` 구동 로직에 `llama_cpp.llama_supports_gpu_offload()` 파이썬 패키지 가속 검증을 추가하여 CPU 전용 패키지 주입 시 Fail-Fast 2중 방어선 구축

**Independent Test**: `.venv` 패키지가 CPU 전용 모드일 때 `./start_server.sh` 구동 시 명시적 에러와 함께 즉시 실패(Fail-Fast)하여 백그라운드 구동을 차단하는지 확인

### Tests for User Story 2
- [X] T008 [P] [US2] Add integration test `test_start_server_preflight_fail_fast()` in `tests/integration/test_migration_pipeline.py`

### Implementation for User Story 2
- [X] T009 [US2] Update `check_hardware_preflight()` in `src/core/cpu_detector.py` to verify `llama_cpp.llama_supports_gpu_offload()`
- [X] T010 [US2] Update `start_server.sh` script generation in `scripts/setup.sh` for Fail-Fast protection
- [X] T011 [US2] Verify T008 integration test passes green in `tests/integration/test_migration_pipeline.py`

**Checkpoint**: User Story 2 complete - 2-tier pre-flight Fail-Fast defense operational in start_server.sh & status_server.sh

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Real environment execution verification and full regression suite pass

- [X] T012 Perform non-interactive real script execution test using `NON_INTERACTIVE=1 scripts/setup.sh`
- [X] T013 Run full unit and integration regression test suite using `uv run pytest tests/unit tests/integration -v`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Story 1 (Phase 3)**: Depends on Foundational completion (P1 MVP)
- **User Story 2 (Phase 4)**: Depends on User Story 1 completion (P1 MVP)
- **Polish (Phase 5)**: Depends on all user stories completion
