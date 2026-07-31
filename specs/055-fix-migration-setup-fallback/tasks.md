# Tasks: 이관 서버 환경 setup.sh Fast-Track 검증 예외 안전성 및 소스 컴파일 Fallback 보장 (055-fix-migration-setup-fallback)

**Input**: Design documents from `/specs/055-fix-migration-setup-fallback/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Includes exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initial analysis and foundational script preparation

- [X] T001 Inspect `scripts/setup.sh` and `scripts/make_seed_pack.sh` for subshell error points
- [X] T002 [P] Verify platform state parameters in `src/core/cpu_detector.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core script CLI option infrastructure that MUST be complete before user story implementation

- [X] T003 Implement CLI argument parsing for `--wheel-path <PATH>` and `--skip-build` in `scripts/setup.sh`
- [X] T004 [P] Enhance 3-way platform state validation helper in `scripts/verify_wheel_binary.py`

---

## Phase 3: User Story 1 - Fast-Track 휠 검증 서브쉘 set -e 방어 & C++ 소스 컴파일 Fallback (Priority: P1) 🎯 MVP

**Goal**: Fast-Track 사전 빌드 휠 검증 서브쉘에 `2>&1 || true` 에러 가드를 적용하여 `set -e` 구문에 의한 스크립트 중단을 방지하고, 사전 휠 검증 실패 시 `DETECTED_CMAKE_ARGS` 기반 C++ 소스 컴파일 파이프라인으로 안전하게 Fallback하여 100% CUDA 가속 설치를 완결

**Independent Test**: Fast-Track 휠 GPU 검증이 False/SIGILL을 반환하도록 설정한 상태에서 `scripts/setup.sh` 실행 시, 스크립트 튕김 없이 `[FAST-TRACK FAIL]` 경고 후 C++ 소스 컴파일로 전이되는지 단위 테스트로 검증

### Tests for User Story 1
- [X] T005 [P] [US1] Write failing unit test `test_setup_subshell_error_guard_and_fallback()` in `tests/unit/test_seed_pack.py`

### Implementation for User Story 1
- [X] T006 [US1] Add `2>&1 || true` error guard to subshell wheel verification in `scripts/setup.sh`
- [X] T007 [US1] Implement 4-tier wheel resolution logic (`--wheel-path` -> `.venv` -> `wheels/` -> C++ compile) in `scripts/setup.sh`
- [X] T008 [US1] Implement 3-way platform state verification (CPU SIMD, CUDA offload, Compute Cap) in `scripts/setup.sh`
- [X] T009 [US1] Support `--wheel-path` argument in `scripts/make_seed_pack.sh`
- [X] T010 [US1] Verify T005 unit test passes green (Red -> Green) in `tests/unit/test_seed_pack.py`

**Checkpoint**: User Story 1 complete - Fast-Track 서브쉘 에러 가드 및 C++ 소스 컴파일 Fallback 정상 작동

---

## Phase 4: User Story 2 - setup.sh 완결성 및 루트 제어 심볼릭 링크 확정 생성 (Priority: P1) 🎯 MVP

**Goal**: `setup.sh` 완결 단계에서 레포지토리 루트 디렉터리에 `./start_server.sh`, `./stop_server.sh`, `./status_server.sh` 심볼릭 링크 생성을 보장하여 사용자 제어 편의성 100% 제공

**Independent Test**: `./setup.sh` 실행 후 루트 디렉터리 내 `./start_server.sh`, `./stop_server.sh`, `./status_server.sh` 파일이 심볼릭 링크로 연결되어 정상 구동되는지 확인

### Tests for User Story 2
- [X] T011 [P] [US2] Write unit test `test_setup_root_symlinks_creation()` in `tests/unit/test_seed_pack.py`

### Implementation for User Story 2
- [X] T012 [US2] Update Step 4 in `scripts/setup.sh` to unconditionally generate root symlinks for `start_server.sh`, `stop_server.sh`, `status_server.sh`
- [X] T013 [US2] Verify T011 unit test passes green (Red -> Green) in `tests/unit/test_seed_pack.py`

**Checkpoint**: User Story 2 complete - Root symlinks generated reliably after setup execution

---

## Phase 5: User Story 3 - 이관 타겟 머신에서의 100% CUDA 가속 검증 및 회귀 테스트 강화 (Priority: P2)

**Goal**: 이관 타겟 서버(Intel i7-930 + GTX 1070) 및 개발 환경에서 100% CUDA GPU 가속 수록 검증 및 `status_server.sh` 헬스 리포트 연동 강화

**Independent Test**: `./status_server.sh` 구동 시 `llama-cpp-python GPU: ✓ CUDA 가속 활성` 및 GPU 컴퓨트 프로세스 연동 확인

### Tests for User Story 3
- [X] T014 [P] [US3] Add integration test for fallback pipeline & status check in `tests/integration/test_migration_pipeline.py`

### Implementation for User Story 3
- [X] T015 [US3] Update `scripts/status_server.sh` to report 3-way platform state and CUDA GPU acceleration status
- [X] T016 [US3] Verify T014 integration test passes green in `tests/integration/test_migration_pipeline.py`

**Checkpoint**: User Story 3 complete - 100% CUDA acceleration verified via status report

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Real environment execution verification and full regression suite pass

- [X] T017 Perform non-interactive real script execution test using `NON_INTERACTIVE=1 scripts/setup.sh`
- [X] T018 Run full unit and integration regression test suite using `uv run pytest tests/unit tests/integration -v`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion (P1 MVP)
- **User Story 2 (Phase 4)**: Depends on User Story 1 completion (P1 MVP)
- **User Story 3 (Phase 5)**: Depends on User Story 1 & 2 completion
- **Polish (Phase 6)**: Depends on all user stories completion

---

## Implementation Strategy

### MVP First (User Story 1 & 2)

1. Complete Phase 1 (Setup) & Phase 2 (Foundational)
2. Complete Phase 3 (User Story 1: Subshell error guard & Fallback)
3. Complete Phase 4 (User Story 2: Root symlinks)
4. **VALIDATE**: Run unit tests in `tests/unit/test_seed_pack.py`
5. Proceed to Phase 5 (User Story 3) and Phase 6 (Polish)
