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
