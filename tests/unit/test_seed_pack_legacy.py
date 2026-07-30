"""
Unit tests for i7-930 prebuilt legacy wheel seed pack packaging and setup fast-track installation pipeline.
"""
import os
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path
import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MAKE_SEED_PACK_SCRIPT = REPO_ROOT / "scripts" / "make_seed_pack.sh"
SETUP_SCRIPT = REPO_ROOT / "scripts" / "setup.sh"


def test_make_seed_pack_script_exists():
    """Verify make_seed_pack.sh and setup.sh exist."""
    assert MAKE_SEED_PACK_SCRIPT.exists()
    assert SETUP_SCRIPT.exists()


def test_make_seed_pack_includes_legacy_wheels_directory(tmp_path):
    """
    Test that make_seed_pack.sh generates a tarball that includes the wheels/legacy_i7_930 directory
    and does NOT exclude wheels/ from the archive (FR-001 / D1 remediation).
    """
    out_tar = tmp_path / "test_seed.tar.gz"
    
    # Ensure wheels/legacy_i7_930 exists in repo
    legacy_dir = REPO_ROOT / "wheels" / "legacy_i7_930"
    legacy_dir.mkdir(parents=True, exist_ok=True)
    
    # Run make_seed_pack.sh with custom output path
    res = subprocess.run(
        [str(MAKE_SEED_PACK_SCRIPT), "-o", str(out_tar)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True
    )
    assert res.returncode == 0, f"make_seed_pack.sh failed: {res.stderr}"
    assert out_tar.exists()

    # Check tarball contents
    with tarfile.open(out_tar, "r:gz") as tar:
        names = tar.getnames()
        # Must include wheels or wheels/legacy_i7_930/.gitkeep
        has_wheels = any("wheels/legacy_i7_930" in name for name in names)
        assert has_wheels, f"wheels/legacy_i7_930 was not included in seed pack archive: {names[:10]}"


def test_make_seed_pack_cli_options():
    """Test make_seed_pack.sh CLI options for --build-legacy and --skip-legacy-build."""
    res = subprocess.run(
        [str(MAKE_SEED_PACK_SCRIPT), "--help"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True
    )
    assert res.returncode == 0
    assert "--build-legacy" in res.stdout
    assert "--skip-legacy-build" in res.stdout


def test_setup_sh_fast_track_and_fallback_logic():
    """Verify setup.sh contains logic for legacy-i7-930 fast-track wheel installation and fallback (FR-002, FR-004)."""
    content = SETUP_SCRIPT.read_text(encoding="utf-8")
    assert "legacy-i7-930" in content
    assert "wheels/legacy_i7_930" in content
    assert "INSTALLED_VIA_FAST_TRACK" in content
    assert "uv pip install" in content


def test_setup_sh_preserves_platform_a_b_compilation():
    """Verify setup.sh retains CMAKE_ARGS source compilation for Platform A/B (FR-003)."""
    content = SETUP_SCRIPT.read_text(encoding="utf-8")
    assert "DETECTED_CMAKE_ARGS" in content
    assert "CMAKE_ARGS=\"$DETECTED_CMAKE_ARGS\" uv pip install" in content
