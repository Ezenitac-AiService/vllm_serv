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


def test_make_seed_pack_script_includes_cuda_arch_and_native_flags():
    """Verify make_seed_pack.sh includes FORCE_CMAKE=1, CMAKE_CUDA_ARCHITECTURES=61, and GGML_NATIVE=OFF (031-fix-seed-pack-cuda-arch FR-001, FR-003)."""
    content = MAKE_SEED_PACK_SCRIPT.read_text(encoding="utf-8")
    assert "FORCE_CMAKE=1" in content
    assert "-DCMAKE_CUDA_ARCHITECTURES=61" in content
    assert "-DGGML_NATIVE=OFF" in content


def test_setup_sh_fast_track_and_fallback_logic():
    """Verify setup.sh contains logic for legacy-i7-930 fast-track wheel installation and fallback (FR-002, FR-004)."""
    content = SETUP_SCRIPT.read_text(encoding="utf-8")
    assert "legacy-i7-930" in content
    assert "wheels/legacy_i7_930" in content
    assert "INSTALLED_VIA_FAST_TRACK" in content
    assert "uv pip install" in content


def test_setup_sh_explicit_llama_cpp_python_wheel_matching():
    """Verify setup.sh explicitly targets llama_cpp_python*.whl instead of generic *.whl (030-fix-legacy-wheel-selection FR-001)."""
    content = SETUP_SCRIPT.read_text(encoding="utf-8")
    # Must use version-sorted ls for llama_cpp_python*.whl
    assert "ls -v wheels/legacy_i7_930/llama_cpp_python*.whl" in content
    assert "tail -n 1" in content


def test_setup_sh_offline_installation_flags():
    """Verify setup.sh uses --no-index --find-links wheels/legacy_i7_930 for offline fast-track wheel installation (030-fix-legacy-wheel-selection FR-002)."""
    content = SETUP_SCRIPT.read_text(encoding="utf-8")
    assert "--no-index" in content
    assert "--find-links wheels/legacy_i7_930" in content


def test_setup_sh_gpu_offload_failure_triggers_fallback():
    """Verify setup.sh falls back to source compilation if GPU offload check fails post Fast-Track (030-fix-legacy-wheel-selection FR-004)."""
    content = SETUP_SCRIPT.read_text(encoding="utf-8")
    # Check that fallback message is logged and source compilation path is reached when Fast-Track or GPU check fails
    assert "Fallback" in content
    assert "CMAKE_ARGS" in content


def test_setup_sh_preserves_platform_a_b_compilation():
    """Verify setup.sh retains CMAKE_ARGS source compilation for Platform A/B (FR-003)."""
    content = SETUP_SCRIPT.read_text(encoding="utf-8")
    assert "DETECTED_CMAKE_ARGS" in content
    assert "CMAKE_ARGS=\"$DETECTED_CMAKE_ARGS\" uv pip install" in content


def test_make_seed_pack_integrates_verify_wheel_binary():
    """Verify make_seed_pack.sh calls verify_wheel_binary.py and --no-build-isolation (035-seed-pack-wheel-diagnostics FR-001)."""
    content = MAKE_SEED_PACK_SCRIPT.read_text(encoding="utf-8")
    assert "verify_wheel_binary.py" in content
    assert "--no-build-isolation" in content
    assert "rm -f wheels/legacy_i7_930/*.whl" in content


def test_setup_sh_fast_track_failure_diagnostic_logging():
    """Verify setup.sh captures GPU check output and logs structured failure cause without 2>/dev/null (035-seed-pack-wheel-diagnostics FR-002)."""
    content = SETUP_SCRIPT.read_text(encoding="utf-8")
    assert "GPU_CHECK_OUTPUT=" in content
    assert "2>/dev/null" not in content.split("llama_supports_gpu_offload")[1].split("fi")[0]
    assert "[FAST-TRACK FAIL]" in content
    assert "FAST-TRACK FAIL TRACEBACK" in content


def test_make_seed_pack_avx_disabling_cmake_flags():
    """Verify make_seed_pack.sh includes all required AVX-disabling CMAKE flags for i7-930 (035-seed-pack-wheel-diagnostics FR-001, T012)."""
    content = MAKE_SEED_PACK_SCRIPT.read_text(encoding="utf-8")
    required_flags = [
        "-DGGML_AVX=OFF",
        "-DGGML_AVX2=OFF",
        "-DGGML_F16C=OFF",
        "-DGGML_FMA=OFF",
        "-DGGML_NATIVE=OFF",
        "-DCMAKE_CUDA_ARCHITECTURES=61",
        "-DGGML_CUDA=ON",
    ]
    for flag in required_flags:
        assert flag in content, f"Missing required CMAKE flag: {flag}"


def test_setup_sh_diagnostic_failure_categories():
    """Verify setup.sh includes all structured failure cause categories (035-seed-pack-wheel-diagnostics FR-002, T012)."""
    content = SETUP_SCRIPT.read_text(encoding="utf-8")
    assert "SIGILL_ILLEGAL_INSTRUCTION" in content
    assert "GPU_OFFLOAD_FALSE" in content
    assert "SHARED_LIB_IMPORT_ERROR" in content


