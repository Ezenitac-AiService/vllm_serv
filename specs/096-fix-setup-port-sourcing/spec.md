# Feature Specification: Fix setup.sh Port Helper Function Sourcing & Production-Grade Shell Architecture

**Feature ID**: 096-fix-setup-port-sourcing  
**Created**: 2026-08-05  
**Status**: APPROVED  

---

## 💡 Overview & User Value

### Problem Statement
When `./setup.sh` is executed via root symlink or directly from working directories outside `scripts/`, `SCRIPT_DIR` was resolving to project root rather than `scripts/`. Consequently, `scripts/common.sh` was not sourced properly, causing `./setup.sh: line 437: get_configured_port: command not found` error during Step 3 (Port Resolution & Firewall Registration).

### User Value
Users and automated deployment scripts running `./setup.sh` on Ubuntu Server 24.04 LTS expect the setup pipeline to complete 100% cleanly without missing shell function errors or non-idempotent side effects.

---

## 🎯 Functional Requirements (FR)

- **FR-001**: System MUST resolve `$BASE_DIR/scripts/common.sh` dynamically to ensure all shell utility functions (`get_configured_port`, `get_configured_host`, `log_info`, `log_warn`, `log_err`) are available to `setup.sh` regardless of invocation path or symlink depth.
- **FR-002**: System MUST gracefully execute Step 3 (Port Resolution & Network Firewall Registration) without crashing on missing helper function calls.
- **FR-003**: System MUST support non-blocking execution mode (`./setup.sh --skip-benchmark`) and complete setup in under 15 seconds.
- **FR-004**: System MUST adhere to Ubuntu Server Shell Best Practices (Google Bash Style Guide compliance, `readlink -f` symlink resolution, and strict `stderr` error logging).
- **FR-005**: System MUST guarantee 100% idempotent execution across repeated runs of `./setup.sh`.

---

## 🎯 Success Criteria (SC)

- **SC-001**: `./setup.sh --skip-benchmark` completes 100% successfully with exit code 0 when invoked from project root via `./setup.sh`.
- **SC-002**: Zero `command not found` or unbound variable errors occur during Step 3 execution.
- **SC-003**: All unit/integration test suites pass without regression (`uv run pytest tests/unit/test_setup_benchmark_integration.py`).
- **SC-004**: Shell execution passes clean ShellCheck / Google Bash Style Guide validation with zero critical lint warnings.

---

## 👥 User Scenarios & Acceptance Criteria

### Scenario 1: Setup Pipeline Execution via Symlink
**Given** the user runs `./setup.sh --skip-benchmark` from the project root `/home/dev/storage/vllm_serv`  
**When** the pipeline reaches Step 3 (Port Resolution & Network Firewall Registration)  
**Then** `get_configured_port main` succeeds, displaying `서빙 포트 설정: 8081/tcp` without `command not found` errors, and setup finishes with exit code 0.

---

## 🧪 Specification Quality Checklist

- [x] No implementation details in core requirements
- [x] Testable and unambiguous acceptance scenarios
- [x] Measurable success criteria
- [x] Bounded feature scope
