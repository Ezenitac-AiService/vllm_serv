# Technical Research & Software Engineering Evaluation: Ubuntu Server Shell Architecture

**Feature ID**: 096-fix-setup-port-sourcing  

## 1. Ubuntu Server 24.04 LTS Shell Scripting Best Practices & Research

### A. Symlink Resolution & Entry-point Determination
- **Canonical Pattern**: Standard Ubuntu/Debian deployment scripts avoid naive `${BASH_SOURCE[0]}` dirname when symlinks exist at root (`./setup.sh -> scripts/setup.sh`).
- **Best Practice Solution**: Resolve anchor files (`pyproject.toml`, `.git`, or `config/`) to determine absolute `$BASE_DIR`, then dynamically source `$BASE_DIR/scripts/common.sh`.

### B. ShellCheck & Google Bash Style Guide Alignment
- Quoting all variable expansions (`"$BASE_DIR/scripts/common.sh"`).
- Explicit signal traps (`set -eo pipefail`) with error handlers on optional subshells.
- Routing all diagnostic messages to `stderr` (`>&2`) to avoid stdout pipeline corruption.

### C. Idempotency & Defensive Programming
- All setup pipeline steps must be 100% idempotent: subsequent invocations must verify existing assets (smart skip) rather than re-downloading or re-initiating background processes.

---

## 2. Decision Matrix & Rationale

| Evaluation Area | Traditional Approach | Modern 2026 Ubuntu Shell Pattern | Selected Approach |
|:---|:---|:---|:---|
| **Symlink Sourcing** | `dirname $0` | Anchor-based `$BASE_DIR` resolution | Dynamic `$BASE_DIR/scripts/common.sh` sourcing |
| **Error Handling** | Bare `set -e` | `set -eo pipefail` with explicit subshell guards | `set -eo pipefail` with `|| true` on optional steps |
| **Logging** | Unformatted `echo` | Timestamped ISO/HH:MM:SS with color codes to stderr | `log_info` / `log_warn` / `log_err` in `common.sh` |
