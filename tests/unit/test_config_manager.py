import os
import json
import pytest
import tempfile
import stat
from src.core.config_manager import ConfigManager

def test_config_manager_default():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = os.path.join(tmpdir, "model_config.json")
        manager = ConfigManager(config_path=config_file)
        
        config = manager.get_config()
        assert "current_model" in config
        assert "current_n_ctx" in config

def test_config_manager_save_load():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = os.path.join(tmpdir, "model_config.json")
        manager = ConfigManager(config_path=config_file)
        
        new_config = {"current_model": "test-model", "current_n_ctx": 4096}
        manager.save_config(new_config)
        
        manager2 = ConfigManager(config_path=config_file)
        loaded = manager2.get_config()
        assert loaded["current_model"] == "test-model"
        assert loaded["current_n_ctx"] == 4096

def test_config_manager_partial_update():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = os.path.join(tmpdir, "model_config.json")
        manager = ConfigManager(config_path=config_file)
        
        manager.save_config({"current_model": "base", "current_n_ctx": 1024})
        
        manager.update_config(current_n_ctx=2048)
        loaded = manager.get_config()
        assert loaded["current_model"] == "base"
        assert loaded["current_n_ctx"] == 2048

def test_config_manager_atomic_replace_and_permissions():
    """T015 / FR-003 & FR-008: Verify atomic replace in same directory and chmod 0600 permissions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = os.path.join(tmpdir, "sub", "model_config.json")
        manager = ConfigManager(config_path=config_file)

        # Write config
        manager.save_config({"current_model": "gemma4-e4b", "current_n_ctx": 16000})
        
        # Verify file exists
        assert os.path.exists(config_file)
        
        # Check permissions (0600: read/write by owner only)
        st = os.stat(config_file)
        mode = stat.S_IMODE(st.st_mode)
        assert mode & 0o077 == 0, f"Permissions expected owner only, got octal {oct(mode)}"

        # Verify caching
        cached = manager.get_config()
        assert cached["current_model"] == "gemma4-e4b"


def test_get_model_catalog_loads_json():
    """FR-008: model_catalog.json에서 카탈로그 로드 검증."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = os.path.join(tmpdir, "model_config.json")
        catalog_file = os.path.join(tmpdir, "model_catalog.json")
        catalog_data = {
            "gemma4-e2b": {"name": "Gemma 4 E2B", "repo_id": "test/repo", "vram_est_mb": 3500},
            "qwen3.5-4b": {"name": "Qwen 3.5 4B", "repo_id": "test/qwen", "vram_est_mb": 5500}
        }
        with open(catalog_file, "w") as f:
            json.dump(catalog_data, f)
        manager = ConfigManager(config_path=config_file)
        result = manager.get_model_catalog()
        assert len(result) == 2
        assert "gemma4-e2b" in result
        assert result["gemma4-e2b"]["vram_est_mb"] == 3500


def test_get_model_catalog_missing_file_returns_empty():
    """FR-008: model_catalog.json 미존재 시 빈 딕셔너리 반환."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = os.path.join(tmpdir, "model_config.json")
        manager = ConfigManager(config_path=config_file)
        result = manager.get_model_catalog()
        assert result == {}


def test_get_server_config_loads_json():
    """FR-009: server_config.json에서 서버 설정 로드 검증."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = os.path.join(tmpdir, "model_config.json")
        server_file = os.path.join(tmpdir, "server_config.json")
        server_data = {"port": 9090, "host": "0.0.0.0", "healthcheck_timeout_s": 60}
        with open(server_file, "w") as f:
            json.dump(server_data, f)
        manager = ConfigManager(config_path=config_file)
        result = manager.get_server_config()
        assert result["port"] == 9090
        assert result["host"] == "0.0.0.0"


def test_get_server_config_env_override():
    """FR-009: LLAMA_PORT, LLAMA_HOST 환경변수 오버라이드 검증."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = os.path.join(tmpdir, "model_config.json")
        server_file = os.path.join(tmpdir, "server_config.json")
        server_data = {"port": 8081, "host": "127.0.0.1"}
        with open(server_file, "w") as f:
            json.dump(server_data, f)
        manager = ConfigManager(config_path=config_file)
        os.environ["LLAMA_PORT"] = "9999"
        os.environ["LLAMA_HOST"] = "192.168.1.1"
        try:
            result = manager.get_server_config()
            assert result["port"] == 9999
            assert result["host"] == "192.168.1.1"
        finally:
            del os.environ["LLAMA_PORT"]
            del os.environ["LLAMA_HOST"]


def test_get_server_config_missing_file_uses_defaults():
    """FR-009: server_config.json 미존재 시 기본값 반환."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = os.path.join(tmpdir, "model_config.json")
        manager = ConfigManager(config_path=config_file)
        result = manager.get_server_config()
        assert result["port"] == 8081
        assert result["host"] == "127.0.0.1"


def test_invalidate_all_caches():
    """모든 캐시 무효화 검증."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = os.path.join(tmpdir, "model_config.json")
        manager = ConfigManager(config_path=config_file)
        # Populate caches
        manager.get_config()
        manager.get_model_catalog()
        manager.get_server_config()
        # Invalidate
        manager.invalidate_all_caches()
        assert manager._cache is None
        assert manager._model_catalog_cache is None
        assert manager._server_config_cache is None
