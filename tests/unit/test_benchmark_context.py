"""Unit tests for benchmark_context_window module.

Features:
- T005: Uncapped binary search range [4096, 16384]
- T012: Binary search step metadata output and SIGKILL/exit code handling
"""

import os
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from scripts.benchmark_context_window import _execute_single_binary_search_inner, run_fine_grained_binary_search


@pytest.mark.asyncio
async def test_uncapped_binary_search_range_execution():
    """T005 [US1]: Verify that binary search search interval expands up to 16384 when VRAM permits."""
    mock_gpu_info = MagicMock()
    mock_gpu_info.total_vram_mb = 16384
    mock_gpu_info.gpu_name = "NVIDIA Test GPU"

    mock_spawn_state = MagicMock()
    mock_spawn_state.status = "READY"
    mock_spawn_state.pid = 99999

    with patch("src.core.cpu_detector.detect_gpu_capability_safe", return_value=mock_gpu_info), \
         patch("src.core.process_manager.ProcessManager.calculate_base_vram_mb", return_value=2000), \
         patch("src.core.process_manager.ProcessManager.spawn_process", new_callable=AsyncMock, return_value=mock_spawn_state), \
         patch("src.core.process_manager.ProcessManager.stop_process", new_callable=AsyncMock), \
         patch("src.core.process_manager.poll_server_health", new_callable=AsyncMock, return_value=True), \
         patch("os.environ.get", side_effect=lambda k, default=None: "1" if k == "MOCK_LLAMA_SERVER" else default):

        res = await _execute_single_binary_search_inner("qwen3.5-2b")
        assert res["is_supported"] is True
        assert res["max_context_length"] >= 4096
        assert len(res["binary_search_steps"]) > 0
        # Check step metadata structure
        step1 = res["binary_search_steps"][0]
        assert "step" in step1
        assert "tested_n_ctx" in step1
        assert "real_vram_mb" in step1
        assert "status" in step1
        assert "reason" in step1


@pytest.mark.asyncio
async def test_sigkill_exception_trapping():
    """T012 [US3]: Verify SIGKILL / Exit Code 137 trapping and step metadata logging."""
    mock_gpu_info = MagicMock()
    mock_gpu_info.total_vram_mb = 16384
    mock_gpu_info.gpu_name = "NVIDIA Test GPU"

    mock_spawn_state = MagicMock()
    mock_spawn_state.status = "ERROR"
    mock_spawn_state.error_message = "Process killed with exit code 137"

    with patch("src.core.cpu_detector.detect_gpu_capability_safe", return_value=mock_gpu_info), \
         patch("src.core.process_manager.ProcessManager.calculate_base_vram_mb", return_value=2000), \
         patch("src.core.process_manager.ProcessManager.spawn_process", new_callable=AsyncMock, return_value=mock_spawn_state), \
         patch("src.core.process_manager.ProcessManager.stop_process", new_callable=AsyncMock), \
         patch("os.environ.get", side_effect=lambda k, default=None: "1" if k == "MOCK_LLAMA_SERVER" else default):

        res = await _execute_single_binary_search_inner("qwen3.5-2b")
        assert len(res["binary_search_steps"]) > 0
        step1 = res["binary_search_steps"][0]
        assert step1["status"] == "OOM/FAIL"
        assert "SIGKILL" in step1["reason"] or "CUDA_OOM_KILLED" in step1["reason"]


def test_evaluate_all_catalog_models_cba_sorting():
    """T003 [US1] (110-benchmark-model-selection-fix): Verify C-B-A hybrid sorting algorithm and dynamic context window selection."""
    from scripts.benchmark_context_window import select_best_model_cba, get_benchmark_metric

    catalog = {
        "gemma4-e2b": {"vram_est_mb": 3759},
        "qwen3.5-4b": {"vram_est_mb": 4000},
        "qwen3.5-9b": {"vram_est_mb": 6229}
    }

    # Case A: qwen3.5-4b has 16384 n_ctx, passes 8K floor, 4B > 2B -> qwen3.5-4b must win over 2b even if 2b has 34816 n_ctx
    mock_results = {
        "gemma4-e2b": {
            "recommended_context_length": 34816,
            "tpot_tok_per_sec": 30.0,
            "peak_vram_mb": 2703,
            "is_supported": True
        },
        "qwen3.5-4b": {
            "recommended_context_length": 16384,
            "tpot_tok_per_sec": 30.0,
            "peak_vram_mb": 4127,
            "is_supported": True
        }
    }

    best_m, best_res = select_best_model_cba(mock_results, catalog)
    assert best_m == "qwen3.5-4b", "C-B-A algorithm must favor 4B over 2B when both satisfy 8K context floor"
    assert get_benchmark_metric(best_res, "recommended_context_length") == 16384

    # Case B: 8K Graceful Fallback - No model reaches 8K context, but models reach 4096. 4B model must win.
    mock_results_sub8k = {
        "gemma4-e2b": {
            "recommended_context_length": 4096,
            "tpot_tok_per_sec": 30.0,
            "peak_vram_mb": 2703,
            "is_supported": True
        },
        "qwen3.5-4b": {
            "recommended_context_length": 4096,
            "tpot_tok_per_sec": 30.0,
            "peak_vram_mb": 4127,
            "is_supported": True
        }
    }
    best_m_sub, best_res_sub = select_best_model_cba(mock_results_sub8k, catalog)
    assert best_m_sub == "qwen3.5-4b", "8K Graceful Fallback must degrade floor to 4096 and select higher quality model"
    assert get_benchmark_metric(best_res_sub, "recommended_context_length") == 4096


def test_benchmark_result_schema_consistency():
    """T007 [US2] (110-benchmark-model-selection-fix): Verify metric dereferencing helper consistency across dictionary key variations."""
    from scripts.benchmark_context_window import get_benchmark_metric

    res1 = {"tpot_tok_per_sec": 35.5, "recommended_context_length": 16384, "peak_vram_mb": 4000, "is_supported": True}
    assert get_benchmark_metric(res1, "benchmark_tps") == 35.5
    assert get_benchmark_metric(res1, "recommended_context_window") == 16384
    assert get_benchmark_metric(res1, "vram_used_mb") == 4000

    res2 = {"benchmark_tps": 28.0, "recommended_context_window": 8192, "vram_used_mb": 3500, "is_supported": True}
    assert get_benchmark_metric(res2, "tpot_tok_per_sec") == 28.0
    assert get_benchmark_metric(res2, "recommended_context_length") == 8192
    assert get_benchmark_metric(res2, "peak_vram_mb") == 3500

