"""Unit tests for model switch sample scripts (sample_04_model_switch.py & openai_04_model_switch.py).

Feature: 116-fix-model-switching
"""

import pytest
from unittest.mock import patch, MagicMock
from sample.common import get_available_llm_models, load_sample_config


def test_get_available_llm_models_filters_non_llm_models():
    """Verify get_available_llm_models returns only LLM models, filtering embedding/reranker models."""
    mock_models_response = {
        "object": "list",
        "data": [
            {"id": "qwen3.5-4b"},
            {"id": "qwen3.5-2b"},
            {"id": "bge-m3"},
            {"id": "bge-reranker-v2-m3"}
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_models_response

    with patch("httpx.get", return_value=mock_resp):
        models = get_available_llm_models()
        assert "qwen3.5-4b" in models
        assert "qwen3.5-2b" in models
        assert "bge-m3" not in models
        assert "bge-reranker-v2-m3" not in models


def test_sample_config_benchmarks_contains_target_models():
    """Verify sample config contains benchmark profiles for target models."""
    config = load_sample_config()
    benchmarks = config.get("model_benchmarks", {})
    assert "qwen3.5-4b" in benchmarks
    assert "qwen3.5-2b" in benchmarks
