# Tasks: uv 기반 가상환경 및 패키지 관리 리팩토링

**Input**: Design documents from `/specs/005-uv-package-management/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Project root: `/home/dev/storage/vllm_serv/`
- Source code: `src/`
- Tests: `tests/`
- Configuration: `pyproject.toml`, `uv.lock`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and `pyproject.toml` / `uv.lock` base setup

- [x] T001 Initialize `pyproject.toml` with project metadata and base configuration in `pyproject.toml`
- [x] T002 Generate `uv.lock` and initialize `.venv` virtualenv using `uv sync`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T003 Verify `.venv` structure and ensure `.gitignore` excludes `.venv/` in `.gitignore`

---

## Phase 3: User Story 1 - uv 기반 신규 패키지 추가 및 의존성 고정 (Priority: P1) 🎯 MVP

**Goal**: `uv add`를 이용하여 메인 및 개발 의존성을 추가하고 `pyproject.toml` 및 `uv.lock`에 고정 조율한다.

**Independent Test**: `uv add` 명령 실행 후 `pyproject.toml` 및 `uv.lock`에 해당 패키지와 버전에 포함되는지 확인한다.

### Implementation for User Story 1

- [x] T004 [P] [US1] Add core production dependencies (`fastapi`, `httpx`, `sse-starlette`, `uvicorn`, `pydantic`) using `uv add` into `pyproject.toml` and `uv.lock`
- [x] T005 [P] [US1] Add development dependencies (`pytest`, `pytest-asyncio`, `anyio`) using `uv add --dev` into `pyproject.toml` and `uv.lock`
- [x] T006 [US1] Verify lockfile integrity and sync state with `uv lock --check`

**Checkpoint**: User Story 1 complete - packages managed via `uv add` and locked in `uv.lock`.

---

## Phase 4: User Story 2 - uv sync를 통한 일관된 가상환경 복구 (Priority: P1)

**Goal**: 단일 명령어 `uv sync`를 사용하여 깨끗한 가상환경(.venv)을 수 초 내에 완전 동기화 복구한다.

**Independent Test**: `.venv` 디렉토리 삭제 후 `uv sync` 실행 시 프로젝트 의존성이 100% 동일하게 복구되는지 검증한다.

### Implementation for User Story 2

- [x] T007 [US2] Test clean environment restoration by removing `.venv` and running `uv sync`
- [x] T008 [US2] Verify environment synchronization and package list match `uv.lock` exactly

**Checkpoint**: User Story 2 complete - `uv sync` environment restoration verified.

---

## Phase 5: User Story 3 - 프로젝트 빌드/테스트 스크립트 uv 호환 리팩토링 (Priority: P2)

**Goal**: 테스트 실행 및 가이드 문서를 `uv run` 기반 커맨드로 일관되게 정립한다.

**Independent Test**: `uv run pytest` 명령으로 10개 전체 테스트 스위트가 수동 activation 없이 정상 통과함을 검증한다.

### Implementation for User Story 3

- [x] T009 [US3] Verify full test suite passes under `uv run pytest` in `tests/`
- [x] T010 [P] [US3] Update Quickstart documentation in `specs/005-uv-package-management/quickstart.md` to reference `uv` CLI workflows

**Checkpoint**: User Story 3 complete - `uv run pytest` integration and documentation updated.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and cleanup across all stories

- [x] T011 [P] Run full validation scenario check per `quickstart.md`
- [x] T012 Cleanup legacy activation scripts and verify no unmanaged dependencies remain

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on US1 completion
- **User Story 3 (Phase 5)**: Depends on US2 completion
- **Polish (Phase 6)**: Depends on all user stories being complete

### Parallel Opportunities

- T004 and T005 can run in parallel (or sequentially via uv CLI)
- T010 documentation update can run in parallel with T009

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup & Phase 2: Foundational
2. Complete Phase 3: User Story 1 (`uv add` dependencies)
3. **STOP and VALIDATE**: Verify `pyproject.toml` and `uv.lock`

### Incremental Delivery

1. Setup + Foundational -> Infrastructure ready
2. User Story 1 -> Package management via `uv add`
3. User Story 2 -> Virtualenv recovery via `uv sync`
4. User Story 3 -> Test execution via `uv run pytest`
