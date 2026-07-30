# Quickstart & Validation Guide: 시드 팩 마이그레이션 및 setup.sh 관리자 권한·방화벽 자동화

**Feature Branch**: `039-seed-pack-sudo-firewall-migration`  
**Created**: 2026-07-30  
**Status**: Draft  

---

## Prerequisites

1. **Target Environment**: Linux Host (Ubuntu, Debian, Rocky Linux, RHEL, CentOS, Arch, etc.)
2. **User Account**: Sudoer account with interactive or passwordless sudo privileges
3. **Python Environment**: `uv` installed or auto-installed via `setup.sh`

---

## Validation Scenarios

### Scenario 1: Interactive `./setup.sh` Run & Sudo Keepalive Verification
Validate interactive sudo credential acquisition and background keepalive loop.

```bash
# 1. Run setup.sh from non-root account in TTY terminal
./scripts/setup.sh

# 2. Expected Behavior:
# - Step 0 prompts for sudo password once (`sudo -v`).
# - Background daemon (`while true; do sudo -n true; sleep 50; done &`) keeps sudo timestamp active.
# - Firewall rules for 8081/tcp and 8089/tcp are applied via ufw/firewalld/nftables/iptables without additional password prompts.
# - Upon completion, background keepalive daemon is automatically killed via signal trap.
```

---

### Scenario 2: `sudo ./setup.sh` Execution & Ownership Auto-Remediation
Validate `$SUDO_USER` detection and ownership normalization for `.venv/`, `logs/`, and `config/`.

```bash
# 1. Run setup.sh explicitly with sudo
sudo ./scripts/setup.sh

# 2. Verify file ownership in workspace
ls -ld .venv logs config

# 3. Expected Result:
# All directories are owned by $SUDO_USER:$SUDO_USER (not root:root).
# Running normal user commands (e.g. `./start_server.sh`) succeeds without Permission Denied errors.
```

---

### Scenario 3: Non-Interactive (CI/CD) Fallback Script Generation
Validate non-interactive environment fallback and `scripts/configure_firewall.sh` helper script creation.

```bash
# 1. Simulate non-interactive execution without TTY
./scripts/setup.sh </dev/null

# 2. Expected Result:
# - Script does not hang waiting for password.
# - `scripts/configure_firewall.sh` is generated with chmod +x permissions.
# - Warning banner with `sudo ./scripts/configure_firewall.sh` instructions is printed.
# - Exit code is 0 (Fail-safe continuation).

# 3. Test running the generated helper script manually
sudo ./scripts/configure_firewall.sh
```

---

### Scenario 4: Seed Pack Packaging & Offline Migration Test
Validate seed pack bundling with updated firewall automation.

```bash
# 1. Build seed pack archive
bash scripts/make_seed_pack.sh

# 2. Verify tarball contents
tar -tzvf vllm_serv_seed_pack.tar.gz | grep configure_firewall

# 3. Expected Result:
# `scripts/configure_firewall.sh` and updated `setup.sh` are contained in the seed pack.
```

---

### Scenario 5: Real-Execution Anti-Mock Test Suite (Constitution v1.3.1)
Run real-execution test suite to verify physical socket probes and OS firewall rule queries.

```bash
# Execute real unit and shell script tests with uv
uv run pytest tests/unit/test_firewall_manager_real.py tests/unit/test_shell_scripts.py -v
```
