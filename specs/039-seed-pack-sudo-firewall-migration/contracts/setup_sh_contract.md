# Interface Contract: `scripts/setup.sh`

**Feature Branch**: `039-seed-pack-sudo-firewall-migration`  
**Artifact Path**: `specs/039-seed-pack-sudo-firewall-migration/contracts/setup_sh_contract.md`  

---

## 1. Command Execution Interface

### Synopsis
```bash
./scripts/setup.sh [OPTIONS]
# 또는
sudo ./scripts/setup.sh [OPTIONS]
```

---

## 2. Execution Flow & Interactive Requirements

### Step 0: Sudo Credential Acquisition & Keep-Alive
- **TTY Environment (`[ -t 0 ]`)**:
  - Run `sudo -v` at script initiation.
  - Prompt user for sudo password once if credentials are expired.
  - Spawn background keep-alive process:
    ```bash
    (while true; do sudo -n true 2>/dev/null; sleep 50; done) &
    SUDO_KEEPALIVE_PID=$!
    trap 'kill $SUDO_KEEPALIVE_PID 2>/dev/null || true' EXIT INT TERM
    ```
- **Non-TTY / Non-Interactive Environment**:
  - Check if `sudo -n true 2>/dev/null` succeeds.
  - If passwordless sudo is available, execute firewall commands with `sudo`.
  - If sudo fails, do NOT block or fail hard. Mark firewall phase as "Deferred" and generate `scripts/configure_firewall.sh`.

---

## 3. Exit Codes & Banner Contracts

| Exit Code | Condition | Description |
|-----------|-----------|-------------|
| `0` | Success | Complete setup finished, all steps (or safe fallback) completed. |
| `1` | Missing Required Files / No nvcc / Hard Fail | Missing essential source files or missing CUDA toolkit (`nvcc`). |

### Non-Interactive Sudo Missing Warning Banner Contract
When sudo is not acquired in a non-interactive environment, `setup.sh` MUST print the following warning box:

```text
========================================================================
⚠️ OS 방화벽 자동 개방 실패 (비대화형 / sudo 권한 부족)
------------------------------------------------------------------------
자동으로 복구 스크립트가 생성되었습니다: scripts/configure_firewall.sh
서버 서비스 포트(8081/tcp, 8089/tcp)를 개방하려면 관리자 권한으로 실행하세요:

    sudo ./scripts/configure_firewall.sh

========================================================================
```

---

## 4. Ownership Auto-Remediation Contract

When executed via `sudo ./setup.sh` (where `$SUDO_USER` is defined and not `root`):
- At the end of `setup.sh` (Step Final):
  - Execute: `chown -R "$SUDO_USER:$SUDO_USER" "$BASE_DIR/.venv" "$BASE_DIR/logs" "$BASE_DIR/config"`
  - Print Info Log: `[SETUP INFO] root 실행 감지: $SUDO_USER 계정으로 소유권 자동 환원 완료.`
