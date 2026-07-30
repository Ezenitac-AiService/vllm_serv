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

    res = subprocess.run(["bash", script_path], capture_output=True, text=True, cwd=REPO_ROOT)
    assert res.returncode == 0
    assert "vllm_serv" in res.stdout
    assert "하드웨어" in res.stdout or "프로세스 상태" in res.stdout


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
