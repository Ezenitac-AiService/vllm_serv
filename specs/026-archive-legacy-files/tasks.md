# Tasks: 코드베이스 리팩토링 및 레거시 파일 .legacy 디렉토리 격리 정돈 (026-archive-legacy-files)

**Input**: Design documents from `/specs/026-archive-legacy-files/`

**Prerequisites**: [plan.md](file:///home/dev/storage/vllm_serv/specs/026-archive-legacy-files/plan.md), [spec.md](file:///home/dev/storage/vllm_serv/specs/026-archive-legacy-files/spec.md), [research.md](file:///home/dev/storage/vllm_serv/specs/026-archive-legacy-files/research.md), [data-model.md](file:///home/dev/storage/vllm_serv/specs/026-archive-legacy-files/data-model.md), [quickstart.md](file:///home/dev/storage/vllm_serv/specs/026-archive-legacy-files/quickstart.md)

**Tests**: 테스트 코드는 헌장 II원칙(테스트 주도 개발 및 품질 보증)에 따라 리팩토링 전후 100% pytest 통과를 지속 검증합니다.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [TaskID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (`[US1]`, `[US2]`, `[US3]`)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project configuration layout & archive directory creation

- [x] T001 Verify project structure and specification files at `specs/026-archive-legacy-files/`
- [x] T002 Create `.legacy/` archive directory at project root

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Base test structures and architecture verification scaffolding

- [x] T003 [P] Create unit test scaffold for root archive cleanliness and modularity in `tests/unit/test_architecture_modularity.py`

**Checkpoint**: Foundation ready - `.legacy/` directory and test harnesses ready.

---

## Phase 3: User Story 1 - 프로젝트 루트 레거시 및 임시 파일 .legacy 아카이브 격리 (Priority: P1) 🎯 MVP

**Goal**: Move obsolete extraction scripts, get-pip.py, benchmark results, and root shell stubs to `.legacy/`.

**Independent Test**: `ls -la .legacy/` lists all target legacy files, and root directory is clean.

- [x] T004 [P] [US1] Move legacy extraction items (`ATEAM_ExtractionItem.py`, `BTEAM_ExtractionItem.py`) to `.legacy/`
- [x] T005 [P] [US1] Move legacy installation script (`get-pip.py`) and benchmark result (`benchmark_results.json`) to `.legacy/`
- [x] T006 [P] [US1] Move 1-line root shell stub scripts (`make_seed_pack.sh`, `setup.sh`, `start_server.sh`, `status_server.sh`, `stop_server.sh`) to `.legacy/`

**Checkpoint**: User Story 1 (Legacy archiving) is complete.

---

## Phase 4: User Story 2 - 소스코드 모듈화 및 코드베이스 리팩토링 (Priority: P1) 🎯 MVP

**Goal**: Audit `src/` and `scripts/` to clean up unused imports, dead code, and redundant helper logic while ensuring 100% pytest pass rate.

**Independent Test**: `uv run pytest tests/` passes 100% cleanly without module import errors.

- [x] T007 [P] [US2] Audit and clean up unused imports and dead code in `src/core/config_manager.py` and `src/core/process_manager.py`
- [x] T008 [P] [US2] Audit and clean up unused imports and dead code in `src/api/server.py` and `src/api/routes/`
- [x] T009 [P] [US2] Refactor and harmonize utility functions in `scripts/` operational scripts

**Checkpoint**: User Story 2 (Codebase refactoring) is complete.

---

## Phase 5: User Story 3 - Git 및 .gitignore 아카이브 경로 보존 규정 적용 (Priority: P2)

**Goal**: Ensure `.legacy/` directory is properly tracked/managed in Git and project documentation is updated.

**Independent Test**: `git status` verifies `.legacy/` files are tracked properly in Git.

- [x] T010 [P] [US3] Verify `.gitignore` configuration for `.legacy/` tracking and archive retention
- [x] T011 [US3] Update project documentation (`README.md`) to reflect `.legacy/` archive directory structure

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification, import audit, and test execution

- [x] T012 [P] Verify import integrity across all codebase modules (`src/`, `scripts/`, `tests/`)
- [x] T013 Run complete pytest test suite (`uv run pytest tests/`) to ensure 100% test pass rate
- [x] T014 Execute quickstart validation guide scenarios in `specs/026-archive-legacy-files/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Stories (Phase 3+)**: Depend on Foundational phase completion
  - User Story 1 (P1) & User Story 2 (P1) can run in parallel or sequentially
  - User Story 3 (P2) depends on US1/US2 completion
- **Polish (Final Phase)**: Depends on all user stories being complete

---

## Implementation Strategy

### MVP First (User Stories 1 & 2)

1. Complete Phase 1: Setup & Phase 2: Foundational
2. Complete Phase 3: User Story 1 (Archive move)
3. Complete Phase 4: User Story 2 (Codebase refactoring)
4. **VALIDATE**: Run `uv run pytest tests/`
5. Complete Phase 5 (US3) & Phase 6 (Polish)
