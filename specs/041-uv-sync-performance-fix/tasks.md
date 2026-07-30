# Tasks: setup.sh uv sync 속도 최적화 및 로컬 격리 고속화 (041-uv-sync-performance-fix)

**Input**: Design documents from `/specs/041-uv-sync-performance-fix/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Mandatory per Constitution v1.4.0 (Anti-Mock & strict `uv run` verification).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project specification structure verification

- [x] T001 Verify project specification files and environment in `specs/041-uv-sync-performance-fix/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared test framework structure and test timeout hardening

- [x] T002 [P] Verify shell script test structure and add `timeout=15` safety wrappers in `tests/unit/test_shell_scripts.py`

---

## Phase 3: User Story 1 - setup.sh uv sync 즉시 통과 및 오프라인/고속 동기화 (Priority: P1) 🎯 MVP

**Goal**: 기존 `uv.lock` 및 `.venv` 존재하는 환경에서 `setup.sh` Step 2 실행 시간을 2초 이내로 단축하고 `uv sync --frozen` 및 Fallback 구현

**Independent Test**: `setup.sh` 실행 시 Step 2 소요 시간이 2초 이내이며 `uv.lock` 부재 시 일반 `uv sync`로 Fallback함을 검증

### Tests for User Story 1 (MANDATORY)

- [x] T003 [P] [US1] Add integration & execution speed test for `setup.sh` Step 2 in `tests/unit/test_shell_scripts.py`

### Implementation for User Story 1

- [x] T004 [US1] Implement `uv sync --frozen` with subshell pipeline protection (`if ! uv sync --frozen 2>/dev/null; then ...; fi`) in `scripts/setup.sh`
- [x] T005 [US1] Implement automatic fallback to `uv sync` on lockfile mismatch in `scripts/setup.sh`

**Checkpoint**: User Story 1 is functional and testable independently.

---

## Phase 4: User Story 2 - uv sync 실행 상태 및 진행 시간 투명 로깅 (Priority: P2)

**Goal**: Step 2 진입 시 사용자가 구동 상태를 명확히 알 수 있도록 투명한 터미널 정보 로그 제공

**Independent Test**: `setup.sh` 실행 시 "[SETUP INFO] 가상환경 고속 동기화 중 (uv sync --frozen)..." 메시지 출력 확인

### Tests for User Story 2 (MANDATORY)

- [x] T006 [P] [US2] Add log message pattern test in `tests/unit/test_shell_scripts.py`

### Implementation for User Story 2

- [x] T007 [US2] Update Step 2 info logging text in `scripts/setup.sh`

**Checkpoint**: User Stories 1 AND 2 are functional independently.

---

## Phase 5: Polish & Anti-Mock Verification

**Purpose**: End-to-end verification and quickstart execution

- [x] T008 Execute full test suite using `uv run pytest` across unit and shell tests
- [x] T009 Run end-to-end validation scenarios documented in `specs/041-uv-sync-performance-fix/quickstart.md`
