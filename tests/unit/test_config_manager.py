import pytest
from src.core.config_manager import ConfigManager, ServerConfig, ModelCatalogEntry

def test_pydantic_server_config_defaults():
    cfg = ServerConfig()
    assert cfg.port == 8081
    assert cfg.host == "127.0.0.1"
    assert "192.168.0.0/24" in cfg.allowed_subnets
    assert cfg.vram_limit_mb == 11264

def test_pydantic_server_config_invalid_port():
    with pytest.raises(ValueError):
        ServerConfig(port=90)

def test_config_manager_get_server_config():
    cm = ConfigManager()
    server_cfg = cm.get_server_config()
    assert isinstance(server_cfg, dict)
    assert "port" in server_cfg
    assert "allowed_subnets" in server_cfg
    assert "host" in server_cfg

def test_config_manager_get_model_catalog():
    cm = ConfigManager()
    catalog = cm.get_model_catalog()
    assert isinstance(catalog, dict)
    if "qwen3.5-4b" in catalog:
        entry = catalog["qwen3.5-4b"]
        model_entry = ModelCatalogEntry(**entry)
        assert model_entry.name == "Qwen 3.5 4B"
        assert model_entry.quant_type == "q4_k_m"
