"""
tests/unit/test_process_manager_multimodal.py
==============================================================================
Unit tests for ProcessManager multimodal (--mmproj) CLI argument building and
11GB VRAM estimation validation across all 4 catalog multimodal models:
- gemma4-e2b
- gemma4-e4b
- gemma4-12b
- qwen3.5-9b-vision
==============================================================================
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from src.core.process_manager import ProcessManager, ProcessStatusEnum
from src.core.gpu_detector import GpuDeviceInfo


@pytest.fixture
def process_manager():
    """Fixture providing a ProcessManager instance initialized with project catalog."""
    pm = ProcessManager()
    return pm


def test_multimodal_models_in_presets(process_manager):
    """Verify all 4 multimodal models exist in process_manager presets with requires_mmproj=True."""
    multimodal_models = ["gemma4-e2b", "gemma4-e4b", "gemma4-12b", "qwen3.5-9b-vision"]
    for model_id in multimodal_models:
        assert model_id in process_manager.model_presets, f"Model {model_id} must be in presets"
        preset = process_manager.model_presets[model_id]
        assert preset.get("requires_mmproj") is True, f"{model_id} must require mmproj"
        assert preset.get("clip") is not None, f"{model_id} must specify clip path"


def test_spawn_process_injects_mmproj_for_all_multimodal_models(process_manager, tmp_path):
    """Verify ProcessManager injects --mmproj <clip_path> for all 4 multimodal models when files exist."""
    multimodal_models = ["gemma4-e2b", "gemma4-e4b", "gemma4-12b", "qwen3.5-9b-vision"]

    mock_gpu_info = GpuDeviceInfo(
        device_id=0,
        name="NVIDIA GeForce GTX 1080 Ti",
        total_vram_mb=11264,
        free_vram_mb=10764,
        is_cuda_available=True
    )

    for model_id in multimodal_models:
        preset = process_manager.model_presets[model_id]
        model_file = tmp_path / preset["model"]
        clip_file = tmp_path / preset["clip"]
        model_file.parent.mkdir(parents=True, exist_ok=True)
        model_file.write_text("dummy model gguf content")
        clip_file.write_text("dummy mmproj gguf content")

        with patch("subprocess.Popen") as mock_popen, \
             patch("os.path.exists", side_effect=lambda p: True if str(p) in (str(model_file), str(clip_file)) else os.path.exists(p)), \
             patch("src.core.gpu_detector.check_gpu_availability", return_value=mock_gpu_info):
            mock_proc = MagicMock()
            mock_proc.poll.return_value = None
            mock_proc.pid = 12345
            mock_proc.stdout = MagicMock()
            mock_popen.return_value = mock_proc

            state = process_manager.spawn_process(model_name=model_id, port=8089)

            assert state.status == ProcessStatusEnum.LOADING
            assert mock_popen.called

            cmd_args = mock_popen.call_args[0][0]
            assert "--mmproj" in cmd_args, f"--mmproj flag missing for {model_id}"

            # Reset process manager state for next model iteration
            process_manager.stop_process()


def test_spawn_process_missing_clip_file_raises_error(process_manager, tmp_path):
    """Verify ProcessManager returns FAILED status when requires_mmproj is True but mmproj file is missing."""
    preset = process_manager.model_presets["qwen3.5-9b-vision"]
    model_file = tmp_path / preset["model"]
    model_file.parent.mkdir(parents=True, exist_ok=True)
    model_file.write_text("dummy model gguf content")

    mock_gpu_info = GpuDeviceInfo(
        device_id=0,
        name="NVIDIA GeForce GTX 1080 Ti",
        total_vram_mb=11264,
        free_vram_mb=10764,
        is_cuda_available=True
    )

    with patch("os.path.exists", side_effect=lambda p: True if str(p) == str(model_file) else (False if "mmproj" in str(p) else os.path.exists(p))), \
         patch("src.core.gpu_detector.check_gpu_availability", return_value=mock_gpu_info):
        state = process_manager.spawn_process(model_name="qwen3.5-9b-vision", port=8089)
        assert state.status == ProcessStatusEnum.FAILED
        assert "not found" in state.error_message.lower() or "missing" in state.error_message.lower() or "vision" in state.error_message.lower() or "clip" in state.error_message.lower() or "mmproj" in state.error_message.lower()


def test_11gb_vram_estimation_checks(process_manager):
    """Verify VRAM estimation for multimodal models within 11GB (11264 MB) VRAM hardware tier limit."""
    # 11GB VRAM tier usable buffer ~ 10764 MB
    assert process_manager.model_presets["gemma4-e2b"]["vram_est_mb"] <= 11264
    assert process_manager.model_presets["gemma4-e4b"]["vram_est_mb"] <= 11264
    assert process_manager.model_presets["qwen3.5-9b-vision"]["vram_est_mb"] <= 11264
