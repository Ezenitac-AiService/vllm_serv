"""
Unit tests for GPU and CUDA Detector (src/core/gpu_detector.py).
"""

import pytest
from unittest.mock import patch, MagicMock
from src.core.gpu_detector import (
    check_gpu_availability,
    GpuDeviceInfo,
    VramOffloadStatus,
    GpuAccelerationError,
    VramOverflowError
)


def test_gpu_device_info_models():
    info = GpuDeviceInfo(
        device_id=0,
        name="NVIDIA GeForce GTX 1080 Ti",
        total_vram_mb=11264,
        free_vram_mb=9000,
        is_cuda_available=True
    )
    assert info.device_id == 0
    assert info.name == "NVIDIA GeForce GTX 1080 Ti"
    assert info.total_vram_mb == 11264
    assert info.is_cuda_available is True

    status = VramOffloadStatus(
        model_id="qwen3.5-2b",
        total_layers=28,
        offloaded_layers=28,
        is_fully_offloaded=True,
        offloaded_vram_mb=3000
    )
    assert status.is_fully_offloaded is True
    assert status.offloaded_layers == 28


@patch("shutil.which")
def test_check_gpu_availability_no_nvidia_smi(mock_which):
    mock_which.return_value = None
    with pytest.raises(GpuAccelerationError) as exc_info:
        check_gpu_availability()
    assert "nvidia-smi tool not found" in str(exc_info.value)


@patch("shutil.which")
@patch("subprocess.run")
def test_check_gpu_availability_success(mock_run, mock_which):
    mock_which.return_value = "/usr/bin/nvidia-smi"
    mock_res = MagicMock()
    mock_res.stdout = "NVIDIA GeForce GTX 1080 Ti, 11264, 9500, 580.173.02\n"
    mock_run.return_value = mock_res

    gpu_info = check_gpu_availability()
    assert gpu_info.name == "NVIDIA GeForce GTX 1080 Ti"
    assert gpu_info.total_vram_mb == 11264
    assert gpu_info.free_vram_mb == 9500
    assert gpu_info.is_cuda_available is True
