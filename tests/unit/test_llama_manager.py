import pytest
import asyncio
from src.core.llama_manager import LlamaManager, ServerState
from src.core.config_manager import ConfigManager

@pytest.mark.asyncio
async def test_llama_manager_initial_state():
    cm = ConfigManager()
    lm = LlamaManager(cm)
    assert lm.state == ServerState.UNLOADED
    assert not lm.is_ready()

@pytest.mark.asyncio
async def test_hardware_limits():
    cm = ConfigManager()
    lm = LlamaManager(cm)
    assert lm.vram_total == 24000
    assert "gemma4-12b" in lm.hardware_limits
    assert lm.hardware_limits["gemma4-12b"] == 9500

@pytest.mark.asyncio
async def test_status_event():
    cm = ConfigManager()
    lm = LlamaManager(cm)
    event = lm.get_status_event()
    assert event["event"] == "status"
    assert "UNLOADED" in event["data"]
