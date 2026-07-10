"""
T006: 실제 모델을 로드하는 통합 테스트 (Mock 없이).
가장 작은 모델(gemma4-2b)을 사용하여 모델 로드와 텍스트 생성이 정상 동작하는지 검증합니다.

실행 조건: models/gemma4-2b/ 디렉토리에 .gguf 파일이 존재해야 합니다.
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.llama_manager import LlamaManager
from src.core.config import MODELS_DIR


# 실제 모델 파일이 존재하지 않으면 테스트 전체를 건너뜁니다.
_MODEL_DIR = os.path.join(MODELS_DIR, "gemma4-2b")
_has_model = os.path.isdir(_MODEL_DIR) and any(
    f.endswith(".gguf") for f in os.listdir(_MODEL_DIR)
) if os.path.isdir(_MODEL_DIR) else False

pytestmark = pytest.mark.skipif(
    not _has_model,
    reason="gemma4-2b .gguf 파일이 models/gemma4-2b/ 에 없습니다. download_models.py를 먼저 실행하세요."
)


class TestRealModelLoad:
    """Mock 없이 실제 GGUF 모델을 로드하여 검증하는 통합 테스트."""

    def test_load_model_returns_success(self):
        """실제 모델을 로드하면 status='success'와 양수 load_time_sec가 반환되어야 합니다."""
        mgr = LlamaManager()
        result = mgr.load_model("gemma4-2b")
        assert result["status"] == "success"
        assert result["load_time_sec"] >= 0

    def test_generate_produces_text(self):
        """로드된 모델에 실제 한국어 프롬프트를 넣으면 응답 텍스트가 반환되어야 합니다."""
        mgr = LlamaManager()
        mgr.load_model("gemma4-2b")
        response = mgr.generate(
            messages=[{"role": "user", "content": "안녕하세요, 자기소개 해주세요."}],
            max_tokens=30
        )
        assert "choices" in response
        content = response["choices"][0]["message"]["content"]
        assert isinstance(content, str)
        assert len(content) > 0

    def test_load_unsupported_model_raises(self):
        """지원하지 않는 model_id를 넣으면 ValueError가 발생해야 합니다."""
        mgr = LlamaManager()
        with pytest.raises(ValueError, match="is not supported"):
            mgr.load_model("nonexistent-model")
