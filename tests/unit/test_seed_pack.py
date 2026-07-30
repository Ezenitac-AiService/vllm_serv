"""
Unit tests for Seed Pack generator (scripts/make_seed_pack.sh).
Tests tarball creation, exclusion rules, custom output paths, and --zip format.
"""

import os
import shutil
import subprocess
import tarfile
import zipfile
import pytest


def get_repo_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_make_seed_pack_script_exists_and_executable():
    repo_root = get_repo_root()
    script_path = os.path.join(repo_root, "scripts", "make_seed_pack.sh")
    symlink_path = os.path.join(repo_root, "make_seed_pack.sh")

    assert os.path.exists(script_path), f"Script missing at {script_path}"
    assert os.access(script_path, os.X_OK), "scripts/make_seed_pack.sh must be executable"

    assert os.path.exists(symlink_path), f"Root symlink missing at {symlink_path}"
    assert os.access(symlink_path, os.X_OK), "make_seed_pack.sh symlink must be executable"


def test_make_seed_pack_default_tarball(tmp_path):
    repo_root = get_repo_root()
    output_tar = tmp_path / "vllm_serv_seed.tar.gz"

    cmd = ["bash", os.path.join(repo_root, "scripts", "make_seed_pack.sh"), "-o", str(output_tar)]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=repo_root)

    assert res.returncode == 0, f"make_seed_pack.sh failed: {res.stderr}\nOutput: {res.stdout}"
    assert output_tar.exists(), "Output tar.gz file must exist"

    # Size check (< 10MB = 10,485,760 bytes)
    file_size = output_tar.stat().st_size
    assert file_size < 10 * 1024 * 1024, f"Seed pack file size too large: {file_size} bytes"

    # Inspect tarball contents
    with tarfile.open(output_tar, "r:gz") as tar:
        names = tar.getnames()

        # Mandatory files check
        normalized_names = [n.lstrip("./") for n in names]

        assert any("pyproject.toml" in n for n in normalized_names), "pyproject.toml missing from archive"
        assert any("setup.sh" in n for n in normalized_names), "setup.sh missing from archive"
        assert any("process_manager.py" in n for n in normalized_names), "process_manager.py missing from archive"
        assert any("model_catalog.json" in n for n in normalized_names), "model_catalog.json missing from archive"

        # Excluded directories check
        for n in normalized_names:
            assert not n.startswith("models/") and "/models/" not in n, f"Excluded directory models/ found in archive: {n}"
            assert not n.startswith(".venv/") and "/.venv/" not in n, f"Excluded directory .venv/ found in archive: {n}"
            assert not n.startswith(".bin/") and "/.bin/" not in n, f"Excluded directory .bin/ found in archive: {n}"
            assert not n.startswith("logs/") and "/logs/" not in n, f"Excluded directory logs/ found in archive: {n}"
            assert not n.startswith("__pycache__/") and "/__pycache__/" not in n, f"Excluded __pycache__ found in archive: {n}"
            assert not n.startswith(".git/") and "/.git/" not in n, f"Excluded .git/ found in archive: {n}"


def test_make_seed_pack_zip_format(tmp_path):
    if not shutil.which("zip"):
        pytest.skip("zip command not installed in environment")

    repo_root = get_repo_root()
    output_zip = tmp_path / "vllm_serv_seed.zip"

    cmd = ["bash", os.path.join(repo_root, "scripts", "make_seed_pack.sh"), "--zip", "-o", str(output_zip)]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=repo_root)

    assert res.returncode == 0, f"make_seed_pack.sh --zip failed: {res.stderr}\nOutput: {res.stdout}"
    assert output_zip.exists(), "Output zip file must exist"

    with zipfile.ZipFile(output_zip, "r") as z:
        names = z.namelist()
        normalized_names = [n.lstrip("./") for n in names]

        assert any("pyproject.toml" in n for n in normalized_names), "pyproject.toml missing from zip archive"
        assert any("setup.sh" in n for n in normalized_names), "setup.sh missing from zip archive"

        for n in normalized_names:
            assert not n.startswith("models/") and "/models/" not in n, f"Excluded directory models/ found in zip: {n}"
            assert not n.startswith(".venv/") and "/.venv/" not in n, f"Excluded directory .venv/ found in zip: {n}"
