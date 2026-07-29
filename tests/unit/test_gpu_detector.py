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

from src.core.process_manager import ProcessManager

def test_parse_vram_offload_full_offload():
    line = "llm_load_tensors: offloaded 28/28 layers to GPU"
    status = ProcessManager.parse_vram_offload_log(line, "qwen3.5-2b")
    assert status is not None
    assert status.is_fully_offloaded is True
    assert status.offloaded_layers == 28
    assert status.total_layers == 28

def test_parse_vram_offload_partial_offload():
    line = "llm_load_tensors: offloaded 20/28 layers to GPU"
    status = ProcessManager.parse_vram_offload_log(line, "qwen3.5-2b")
    assert status is not None
    assert status.is_fully_offloaded is False
    assert status.offloaded_layers == 20
    assert status.total_layers == 28

def test_parse_vram_offload_irrelevant_line():
    line = "llm_load_tensors: using CPU backend"
    status = ProcessManager.parse_vram_offload_log(line, "qwen3.5-2b")
    assert status is None

def test_verify_vram_offload_raises_on_partial():
    pm = ProcessManager()
    status = VramOffloadStatus(
        model_id="qwen3.5-2b",
        total_layers=28,
        offloaded_layers=20,
        is_fully_offloaded=False
    )
    with pytest.raises(VramOverflowError, match="VRAM_PARTIAL_OFFLOAD_ERROR: 20/28 layers offloaded. 100% VRAM offload required."):
        pm.verify_vram_offload("qwen3.5-2b", status)

def test_parse_vram_offload_vram_size():
    line = "llm_load_tensors:        CUDA0 model buffer size =  2953.80 MiB"
    status = ProcessManager.parse_vram_offload_log(line, "qwen3.5-2b")
    assert status is not None
    assert status.is_fully_offloaded is True
    assert status.offloaded_vram_mb == 2953


# T018: Dynamic CUDA version detection tests
@patch("src.core.gpu_detector.shutil.which")
@patch("subprocess.run")
def test_check_gpu_availability_dynamic_cuda_version(mock_run, mock_which):
    """T018: check_gpu_availability는 nvidia-smi 일반 출력에서 CUDA 버전을 동적으로 감지해야 한다."""
    def which_side_effect(cmd):
        if cmd == "nvidia-smi":
            return "/usr/bin/nvidia-smi"
        if cmd == "nvcc":
            return None
        return None
    mock_which.side_effect = which_side_effect

    # First call: CSV query; Second call: plain nvidia-smi for CUDA version
    csv_res = MagicMock()
    csv_res.stdout = "NVIDIA GeForce GTX 1080 Ti, 11264, 9500, 580.173.02\n"

    plain_res = MagicMock()
    plain_res.stdout = (
        "+-----------------------------------------------------------------------------+\n"
        "| NVIDIA-SMI 580.173.02    Driver Version: 580.173.02    CUDA Version: 13.0   |\n"
        "+-----------------------------------------------------------------------------+\n"
    )

    mock_run.side_effect = [csv_res, plain_res]

    gpu_info = check_gpu_availability()
    assert gpu_info.cuda_version == "13.0"
    assert gpu_info.is_cuda_available is True


@patch("src.core.gpu_detector.shutil.which")
@patch("subprocess.run")
def test_check_gpu_availability_cuda_version_fallback_none(mock_run, mock_which):
    """T018: CUDA 버전 파싱 실패 시 None으로 폴백해야 한다."""
    def which_side_effect(cmd):
        if cmd == "nvidia-smi":
            return "/usr/bin/nvidia-smi"
        if cmd == "nvcc":
            return None
        return None
    mock_which.side_effect = which_side_effect

    csv_res = MagicMock()
    csv_res.stdout = "NVIDIA GeForce GTX 1080 Ti, 11264, 9500, 580.173.02\n"

    # Plain output without CUDA Version line
    plain_res = MagicMock()
    plain_res.stdout = "Some other nvidia-smi output without CUDA info\n"

    mock_run.side_effect = [csv_res, plain_res]

    gpu_info = check_gpu_availability()
    assert gpu_info.cuda_version is None


# T019: ProcessState.vram_offloaded field tests
from src.core.process_manager import ProcessState, ProcessStatusEnum

def test_process_state_vram_offloaded_default():
    """T019: ProcessState의 vram_offloaded 기본값은 None이어야 한다."""
    state = ProcessState(status=ProcessStatusEnum.LOADING, model_id="qwen3.5-2b")
    assert state.vram_offloaded is None


def test_verify_vram_offload_sets_vram_offloaded_true():
    """T019: verify_vram_offload 성공 시 ProcessState.vram_offloaded=True로 설정되어야 한다."""
    pm = ProcessManager()
    pm.state = ProcessState(
        status=ProcessStatusEnum.LOADING,
        model_id="qwen3.5-2b",
        port=8081,
    )
    status = VramOffloadStatus(
        model_id="qwen3.5-2b",
        total_layers=28,
        offloaded_layers=28,
        is_fully_offloaded=True,
        offloaded_vram_mb=3000,
    )
    pm.verify_vram_offload("qwen3.5-2b", status)
    assert pm.state.vram_offloaded is True


# T021: Runtime VRAM overflow monitoring tests
def test_check_vram_runtime_overflow_safe():
    """T021: VRAM 사용률이 임계치 미만일 때 예외가 발생하지 않아야 한다."""
    pm = ProcessManager()
    with patch("shutil.which", return_value="/usr/bin/nvidia-smi"):
        mock_result = MagicMock()
        mock_result.stdout = "5000, 11264\n"  # ~44% usage
        with patch("subprocess.run", return_value=mock_result):
            pm.check_vram_runtime_overflow(threshold_pct=95.0)  # Should not raise


def test_check_vram_runtime_overflow_raises():
    """T021: VRAM 사용률이 임계치를 초과하면 VramOverflowError가 발생해야 한다."""
    pm = ProcessManager()
    with patch("shutil.which", return_value="/usr/bin/nvidia-smi"):
        mock_result = MagicMock()
        mock_result.stdout = "10800, 11264\n"  # ~95.9% usage
        with patch("subprocess.run", return_value=mock_result):
            with pytest.raises(VramOverflowError, match="VRAM 실시간 오버플로우 감지"):
                pm.check_vram_runtime_overflow(threshold_pct=95.0)


def test_check_vram_runtime_overflow_no_nvidia_smi():
    """T021: nvidia-smi 미설치 환경에서는 검사를 건너뛰어야 한다."""
    pm = ProcessManager()
    with patch("shutil.which", return_value=None):
        pm.check_vram_runtime_overflow(threshold_pct=95.0)  # Should not raise
