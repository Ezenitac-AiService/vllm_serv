"""
Integration tests for GPU CUDA validation, CPU fallback blocking, and VRAM offload status.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from src.core.process_manager import ProcessManager, ProcessStatusEnum
from src.core.gpu_detector import GpuAccelerationError, check_gpu_availability


@pytest.mark.asyncio
async def test_spawn_process_cpu_only_blocked():
    pm = ProcessManager(port=8081)
    os.environ["MOCK_CPU_ONLY"] = "1"
    try:
        state = await pm.spawn_process("qwen3.5-2b", 4096)
        assert state.status == ProcessStatusEnum.ERROR
        assert "GpuAccelerationError" in state.error_message
        assert "CPU-only execution is strictly blocked" in state.error_message
    finally:
        os.environ.pop("MOCK_CPU_ONLY", None)


@pytest.mark.asyncio
async def test_spawn_process_mock_llama_server_gpu_allowed():
    pm = ProcessManager(port=8081)
    os.environ["MOCK_LLAMA_SERVER"] = "1"
    try:
        state = await pm.spawn_process("qwen3.5-2b", 4096)
        assert state.status == ProcessStatusEnum.LOADING
        await pm.stop_process()
        assert pm.state.status == ProcessStatusEnum.UNLOADED
    finally:
        os.environ.pop("MOCK_LLAMA_SERVER", None)
