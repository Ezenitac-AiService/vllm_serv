# Tasks: 시드 팩 마이그레이션 파이프라인 및 ProcessManager 호환성 전수 검증 (Fix Seed Pack Migration Pipeline & ProcessManager Compatibility)

**Input**: Design documents from `/specs/113-fix-seed-pack-migration-scripts/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Exact file paths included in all descriptions.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verification of task environment and feature directory structure

- [x] T001 Verify specification and design documents in `specs/113-fix-seed-pack-migration-scripts/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Unit test suite expansion to capture ProcessManager and script pipeline requirements before implementation

- [x] T002 Add unit test cases for ProcessManager static and instance dual-compatibility in `tests/unit/test_process_manager.py`
- [x] T003 [P] Add unit test cases for expanded required entry checks in `tests/unit/test_seed_pack.py`
- [x] T004 [P] Add unit test cases for setup.sh Step 1 REQUIRED_FILES check in `tests/unit/test_shell_scripts.py`

**Checkpoint**: Foundational test cases ready - implementation phase can now begin.

---

## Phase 3: User Story 1 - 타 플랫폼 마이그레이션 언팩->setup->벤치마크 원스톱 무결성 보장 (Priority: P1) 🎯 MVP

**Goal**: ProcessManager 인터페이스 하위 호환성 보장 및 시드 팩 pack/unpack/setup 스크립트 전수 수록 무결성 검증으로 마이그레이션 크래시 차단

**Independent Test**: `make_seed_pack.sh` -> `unpack_seed.sh` -> `./setup.sh` -> `benchmark_context_window.py` 구동 시 AttributeError 0건 및 스크립트 누락 0건 검증

### Tests for User Story 1

- [x] T005 [P] [US1] Unit test for ProcessManager calculate_base_vram_mb and force_kill_zombie_llama_servers dual calling in `tests/unit/test_process_manager.py`

### Implementation for User Story 1

- [x] T006 [P] [US1] Bind calculate_base_vram_mb and force_kill_zombie_llama_servers as @staticmethod and instance method fallback in `src/core/process_manager.py`
- [x] T007 [P] [US1] Apply getattr and try-except defensive error handling for ProcessManager in `scripts/benchmark_context_window.py`
- [x] T008 [P] [US1] Apply defensive error handling for ProcessManager helper calls in `scripts/benchmark_quality.py`
- [x] T009 [P] [US1] Expand verify_archive_entry list in `scripts/make_seed_pack.sh` to include process_manager.py, model_downloader.py, benchmark_quality.py, benchmark_context_window.py, setup.sh, unpack_seed.sh, make_seed_pack.sh
- [x] T010 [P] [US1] Expand REQUIRED_ENTRIES list in `scripts/unpack_seed.sh` to include process_manager.py, model_downloader.py, benchmark_quality.py, benchmark_context_window.py, setup.sh, make_seed_pack.sh
- [x] T011 [US1] Expand REQUIRED_FILES list in Step 1 of `scripts/setup.sh` to include src/core/model_downloader.py, scripts/benchmark_context_window.py, scripts/unpack_seed.sh

**Checkpoint**: At this point, User Story 1 (MVP) is fully functional and testable independently.

---

## Phase 4: User Story 2 - 시드 팩 패키징 제외/수록 규칙 및 루트 심볼릭 링크 안전 재구성 (Priority: P2)

**Goal**: 대용량 가중치 제외 경량화 아카이브 보장 및 setup.sh 실행 시 루트 심볼릭 링크 안전 원자적 갱신

**Independent Test**: 아카이브 크기 < 50MB 검증 및 `./setup.sh` 구동 후 `./start_server.sh`, `./stop_server.sh`, `./status_server.sh` 심볼릭 링크 정상 동작 확인

### Implementation for User Story 2

- [x] T012 [P] [US2] Verify and enforce exclusion patterns (models/, .venv/, .bin/, logs/, build/, dist/, .git/, .specify/) in `scripts/make_seed_pack.sh`
- [x] T013 [US2] Update Step 4 in `scripts/setup.sh` to safely force relink (ln -sf) root symlinks start_server.sh, stop_server.sh, status_server.sh

**Checkpoint**: User Stories 1 AND 2 are both complete and independently testable.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: End-to-end quickstart validation and full suite regression testing

- [x] T014 Run validation scenarios in `specs/113-fix-seed-pack-migration-scripts/quickstart.md`
- [x] T015 Run full unit regression test suite `uv run pytest tests/unit/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS User Story implementation.
- **User Story 1 (Phase 3)**: Depends on Foundational completion.
- **User Story 2 (Phase 4)**: Depends on Foundational completion (can run after or in parallel with US1).
- **Polish (Phase 5)**: Depends on US1 & US2 implementation completion.

### Parallel Opportunities

- T003, T004 can run in parallel in Phase 2.
- T006, T007, T008, T009, T010 can run in parallel in Phase 3.
- T012 can run in parallel in Phase 4.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & Phase 2 foundational tests.
2. Implement T006~T011 (ProcessManager dual compatibility & script entries).
3. Validate MVP test suite: `uv run pytest tests/unit/test_process_manager.py tests/unit/test_seed_pack.py`.

### Incremental Delivery

1. Complete US1 -> MVP validated.
2. Complete US2 -> Seed pack exclusions & symlink relinking validated.
3. Run Phase 5 polish & full regression test suite.
