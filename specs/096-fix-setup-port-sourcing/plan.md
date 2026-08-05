# Implementation Plan: Fix setup.sh Port Helper Function Sourcing & Production-Grade Shell Architecture

**Feature ID**: 096-fix-setup-port-sourcing  
**Branch**: 096-fix-setup-port-sourcing  
**Created**: 2026-08-05  

---

## Technical Context

- **Target Script**: `scripts/setup.sh`
- **Helper Dependency**: `scripts/common.sh` (`get_configured_port`, `get_configured_host`, `log_info`, `log_warn`, `log_err`)
- **Key Problem**: Sourcing path resolved relative to `BASH_SOURCE[0]` rather than `$BASE_DIR/scripts/common.sh`, resulting in missing function errors when executed via symlink from root (`./setup.sh`).
- **Target OS & Shell**: Ubuntu Server 24.04 LTS, GNU Bash 5.2+

---

## Architecture & Software Engineering Principles

1. **Robust Entry-point Resolution**: Use `$BASE_DIR/scripts/common.sh` as primary source location after resolving `$BASE_DIR` via `pyproject.toml` anchors.
2. **Idempotency & Atomic Execution**: Ensure setup script can be re-run indefinitely without unintended state mutation.
3. **Strict Error Isolation & Telemetry**: Route diagnostic logs to `stderr` and preserve stdout cleanliness for subshell evaluations.

---

## Constitution Check

- **Principle I (Quality First)**: Clean 0-error setup execution.
- **Principle II (Strict Verification)**: Unit tests and bash execution verification.

---

## Proposed Touch-points

- `scripts/setup.sh`: Re-order `common.sh` sourcing to locate `$BASE_DIR/scripts/common.sh` dynamically after `$BASE_DIR` resolution.
- `scripts/common.sh`: Ensure timestamping and `stderr` logging handlers are active.
- `tests/unit/test_setup_benchmark_integration.py`: Verify setup pipeline invocation contract.

---

## Design Artifacts

- `research.md`: Ubuntu Server Shell Best Practices & Sourcing path resolution analysis.
- `quickstart.md`: Verification commands (`./setup.sh --skip-benchmark`).
