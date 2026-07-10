"""
LlamaManager 단위 테스트.
Mock 없이 순수 로직(validation, error path)을 검증합니다.
실제 모델 로드가 필요한 테스트는 tests/integration/test_model_load.py에 있습니다.
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.llama_manager import LlamaManager
from src.core.config import SUPPORTED_MODELS


def test_load_unsupported_model():
    """지원하지 않는 model_id를 넣으면 ValueError가 발생해야 합니다."""
    manager = LlamaManager()
    with pytest.raises(ValueError, match="is not supported"):
        manager.load_model("invalid-model-id")


def test_generate_without_load():
    """모델이 로드되지 않은 상태에서 generate를 호출하면 RuntimeError가 발생합니다."""
    manager = LlamaManager()
    with pytest.raises(RuntimeError, match="No model is currently loaded"):
        manager.generate([{"role": "user", "content": "hello"}])


def test_supported_models_keys():
    """config.py에 정의된 모델이 올바른 key를 갖고 있어야 합니다."""
    assert "gemma4-2b" in SUPPORTED_MODELS
    assert "gemma4-4b" in SUPPORTED_MODELS
    assert "gemma4-12b" in SUPPORTED_MODELS


def test_model_config_has_repo_id():
    """모든 모델 설정에 repo_id가 비어있지 않아야 합니다."""
    for model_id, config in SUPPORTED_MODELS.items():
        assert config.repo_id, f"{model_id}의 repo_id가 비어있습니다."
        assert "google/" in config.repo_id, f"{model_id}의 repo_id가 google/ prefix가 아닙니다."
