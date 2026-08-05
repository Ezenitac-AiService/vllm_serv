# Tasks: Fix setup.sh Port Helper Function Sourcing & Production Shell Architecture

**Feature**: 096-fix-setup-port-sourcing  
**Status**: IN_PROGRESS  

---

## Phase 1: Setup & Foundational

- [X] T001 Inspect `scripts/setup.sh` sourcing path order for `$BASE_DIR/scripts/common.sh`

---

## Phase 2: User Story 1 - Symlink Execution & Port Helper Sourcing Fix

- [X] T002 [P] [US1] Re-order `common.sh` sourcing in `scripts/setup.sh` to resolve `$BASE_DIR/scripts/common.sh` after `$BASE_DIR` determination
- [X] T003 [P] [US1] Verify `get_configured_port` availability during Step 3 execution in `scripts/setup.sh`

---

## Phase 3: Polish & Cross-Cutting Validation (Ubuntu Shell Standards & SW Engineering)

- [X] T004 [P] Run `./setup.sh --skip-benchmark` validation scenario per `quickstart.md`
- [X] T005 [P] Execute unit test suite `uv run pytest tests/unit/test_setup_benchmark_integration.py`
- [X] T006 [P] Verify Google Bash Style Guide & ShellCheck compliance across `scripts/setup.sh` and `scripts/common.sh`

---

## Dependencies & Execution Order

- **Phase 1**: Setup (Blocking prerequisite)
- **Phase 2**: User Story 1 (Core Fix)
- **Phase 3**: Validation, SW Engineering Standards & Test Suite Pass

---

## Implementation Strategy

1. **MVP First**: Complete Phase 2 fix in `scripts/setup.sh`.
2. **Incremental Delivery**: Run Phase 3 validation (`./setup.sh --skip-benchmark` and `pytest`).
