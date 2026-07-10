import os
import json
import pytest
import tempfile
from src.core.config_manager import ConfigManager

def test_config_manager_default():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = os.path.join(tmpdir, "model_config.json")
        manager = ConfigManager(config_path=config_file)
        
        # Should initialize with default if not exist
        config = manager.get_config()
        assert "current_model" in config
        assert "current_n_ctx" in config

def test_config_manager_save_load():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = os.path.join(tmpdir, "model_config.json")
        manager = ConfigManager(config_path=config_file)
        
        # Save custom
        new_config = {"current_model": "test-model", "current_n_ctx": 4096}
        manager.save_config(new_config)
        
        # Load
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
