import pytest
import asyncio
from src.core.llama_manager import LlamaManager, ServerState
from src.core.config_manager import ConfigManager
from src.core.process_manager import ProcessManager, ProcessStatusEnum, ProcessState
from src.core.event_broadcaster import EventBroadcaster, EventPayload

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

@pytest.mark.asyncio
async def test_process_manager_state():
    """T012: Test ProcessManager state encapsulation and immutability."""
    pm = ProcessManager(port=8085)
    assert pm.state.status == ProcessStatusEnum.UNLOADED
    assert pm.get_vram_limit("gemma4-e4b") == 16000
    
    # Test ProcessState immutability
    state = ProcessState(status=ProcessStatusEnum.LOADING, model_id="gemma4-e4b")
    with pytest.raises(Exception):
        state.status = ProcessStatusEnum.READY

@pytest.mark.asyncio
async def test_event_broadcaster_bounded_queue():
    """T012 / FR-011: Test EventBroadcaster listener management and queue overflow handling."""
    eb = EventBroadcaster(queue_maxsize=2)
    q = eb.subscribe(initial_event={"event": "initial"})
    assert q.qsize() == 1
    
    # Broadcast more than queue_maxsize to test overflow handling
    eb.broadcast({"event": "msg1"})
    eb.broadcast({"event": "msg2"})
    eb.broadcast({"event": "msg3"})

    # Queue should be bounded without exception
    assert q.qsize() <= 2
    eb.unsubscribe(q)
