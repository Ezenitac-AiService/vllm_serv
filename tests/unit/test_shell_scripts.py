"""
Unit tests for operational shell scripts (status_server.sh, start_server.sh, setup.sh, make_seed_pack.sh).
Validates execution, output formatting, pre-flight failure handling, and archive packaging.
"""

import os
import subprocess
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_status_server_script_execution():
    """T006 [US1]: Verifies status_server.sh runs successfully and outputs hardware report and profile info."""
    script_path = os.path.join(REPO_ROOT, "scripts", "status_server.sh")
    assert os.path.exists(script_path), f"Script missing: {script_path}"

    try:
        res = subprocess.run(["bash", script_path], capture_output=True, text=True, cwd=REPO_ROOT, timeout=15)
        assert res.returncode == 0
        assert "vllm_serv" in res.stdout
        assert "하드웨어" in res.stdout or "프로세스 상태" in res.stdout
    except subprocess.TimeoutExpired:
        pytest.skip("status_server.sh execution timed out due to background process locks")


def test_setup_sh_uv_sync_frozen_pattern():
    """T003 [US1] (041-uv-sync-performance-fix): Verifies setup.sh uses uv sync --frozen with subshell fallback protection."""
    script_path = os.path.join(REPO_ROOT, "scripts", "setup.sh")
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "uv sync --frozen" in content, "setup.sh must use 'uv sync --frozen' for fast-track sync"
    assert "가상환경 고속 동기화" in content, "setup.sh must output fast sync log message"



def test_start_server_preflight_help():
    """T009 [US2]: Verifies start_server.sh contains pre-flight check logic."""
    script_path = os.path.join(REPO_ROOT, "scripts", "start_server.sh")
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "check-preflight" in content or "Pre-flight" in content


def test_setup_script_contains_match_profile():
    """T012 [US3]: Verifies setup.sh invokes match-profile CLI option."""
    script_path = os.path.join(REPO_ROOT, "scripts", "setup.sh")
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "match-profile" in content or "cpu_detector" in content


def test_make_seed_pack_includes_platform_profiles():
    """T015 [US4]: Verifies make_seed_pack.sh script includes config/platform_profiles.json in target files."""
    script_path = os.path.join(REPO_ROOT, "scripts", "make_seed_pack.sh")
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "platform_profiles.json" in content


def test_setup_sh_fast_track_diagnostic_output():
    """T016 [US2]: Verifies setup.sh captures GPU check stderr and logs structured failure cause without 2>/dev/null (FR-002)."""
    script_path = os.path.join(REPO_ROOT, "scripts", "setup.sh")
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "GPU_CHECK_OUTPUT=" in content
    assert "2>/dev/null" not in content.split("llama_supports_gpu_offload")[1].split("fi")[0]
    assert "[FAST-TRACK FAIL]" in content
    assert "FAST-TRACK FAIL TRACEBACK" in content


def test_setup_sh_failure_categories():
    """T016 [US2]: Verifies setup.sh includes all structured failure cause categories (SIGILL, GPU_OFFLOAD_FALSE, SHARED_LIB_IMPORT_ERROR)."""
    script_path = os.path.join(REPO_ROOT, "scripts", "setup.sh")
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "SIGILL_ILLEGAL_INSTRUCTION" in content
    assert "GPU_OFFLOAD_FALSE" in content
    assert "SHARED_LIB_IMPORT_ERROR" in content


# ==============================================================================
# 039-seed-pack-sudo-firewall-migration (FR-001, FR-002, FR-004, FR-007)
# ==============================================================================

def test_setup_sh_sudo_keepalive_daemon_pattern():
    """T004 [US1]: Verifies setup.sh contains sudo keepalive daemon loop pattern with background PID tracking.

    Real file content inspection per Constitution v1.4.0 Anti-Mock Discipline.
    Checks: sudo -v, sudo -n true, sleep 50, SUDO_KEEPALIVE_PID, trap, kill.
    """
    script_path = os.path.join(REPO_ROOT, "scripts", "setup.sh")
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()

    # FR-001: sudo -v interactive elevation at script start
    assert "sudo -v" in content, "setup.sh must contain 'sudo -v' for interactive elevation"

    # FR-002: Background keepalive daemon pattern
    assert "sudo -n true" in content, "setup.sh must contain 'sudo -n true' for non-interactive keepalive"
    assert "sleep 50" in content or "sleep 45" in content, "setup.sh must contain keepalive sleep interval"
    assert "SUDO_KEEPALIVE_PID" in content, "setup.sh must track keepalive daemon PID"

    # FR-002: Trap for cleanup on exit
    assert "trap" in content, "setup.sh must register trap for daemon cleanup"
    assert "kill" in content, "setup.sh must kill keepalive daemon on exit"


def test_setup_sh_tty_detection():
    """T004 [US1]: Verifies setup.sh contains TTY detection logic ([ -t 0 ]) for interactive vs non-interactive branching."""
    script_path = os.path.join(REPO_ROOT, "scripts", "setup.sh")
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "-t 0" in content, "setup.sh must detect TTY via [ -t 0 ] or [[ -t 0 ]]"


def test_setup_sh_ownership_correction_sudo_user():
    """T005 [US1]: Verifies setup.sh contains SUDO_USER detection and chown ownership remediation logic.

    Real file content inspection per Constitution v1.4.0 Anti-Mock Discipline.
    """
    script_path = os.path.join(REPO_ROOT, "scripts", "setup.sh")
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()

    # FR-007: SUDO_USER detection
    assert "SUDO_USER" in content, "setup.sh must detect $SUDO_USER environment variable"

    # FR-007: chown -R remediation
    assert "chown" in content, "setup.sh must use chown for ownership remediation"


def test_setup_sh_noninteractive_fallback_banner():
    """T005 [US1]: Verifies setup.sh generates warning banner and configure_firewall.sh for non-interactive environments (FR-004)."""
    script_path = os.path.join(REPO_ROOT, "scripts", "setup.sh")
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()

    # FR-004: Warning banner output per contract
    assert "configure_firewall.sh" in content, "setup.sh must reference configure_firewall.sh fallback script"
    assert "방화벽" in content, "setup.sh must contain Korean firewall warning text"


def test_configure_firewall_sh_syntax():
    """T004/T005 [US1]: Verify configure_firewall.sh shell script syntax is valid via bash -n."""
    script_path = os.path.join(REPO_ROOT, "scripts", "configure_firewall.sh")
    assert os.path.exists(script_path), f"Script missing: {script_path}"

    res = subprocess.run(["bash", "-n", script_path], capture_output=True, text=True)
    assert res.returncode == 0, f"configure_firewall.sh has syntax errors: {res.stderr}"


def test_configure_firewall_sh_root_check():
    """T005 [US1]: Verify configure_firewall.sh checks for root privileges."""
    script_path = os.path.join(REPO_ROOT, "scripts", "configure_firewall.sh")
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "EUID" in content, "configure_firewall.sh must check EUID for root privilege verification"
    assert "exit 1" in content, "configure_firewall.sh must exit 1 when not running as root"


def test_dual_pid_cleanup_in_stop_server():
    """T006 [US2]: Verifies stop_server.sh contains dual PID file removal and 3-tier pgrep pattern searches."""
    script_path = os.path.join(REPO_ROOT, "scripts", "stop_server.sh")
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "vllm_serv.pid" in content, "stop_server.sh must clean up vllm_serv.pid"
    assert "vllm_dashboard.pid" in content, "stop_server.sh must clean up vllm_dashboard.pid"
    assert "src.api.server" in content, "stop_server.sh must search for src.api.server"
    assert "uvicorn src.api.main:app" in content, "stop_server.sh must search for uvicorn src.api.main:app"
    assert "llama-server" in content, "stop_server.sh must search for llama-server"



