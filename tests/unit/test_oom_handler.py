"""
T007: OOM 및 런타임 예외를 안전하게 처리하는 테스트.
실제 모델 로드 없이, LlamaManager의 방어 로직을 직접 검증합니다.
Mock을 사용하지 않고 순수 로직만 테스트합니다.
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.llama_manager import LlamaManager
from src.core.config import get_hf_token


class TestOOMHandler:
    """OOM 및 예외 상황에서의 안전한 처리 검증."""

    def test_generate_without_loaded_model_raises(self):
        """모델이 로드되지 않은 상태에서 generate를 호출하면 RuntimeError가 발생해야 합니다."""
        mgr = LlamaManager()
        with pytest.raises(RuntimeError, match="No model is currently loaded"):
            mgr.generate([{"role": "user", "content": "hello"}])

    def test_load_missing_model_dir_raises_file_not_found(self):
        """존재하지 않는 모델 디렉토리 또는 메인 모델 파일이 없으면 예외가 발생해야 합니다."""
        mgr = LlamaManager()
        with pytest.raises((FileNotFoundError, RuntimeError)):
            mgr.load_model("gemma4-12b")  # 12B가 미다운로드이거나 mmproj만 존재

    def test_load_invalid_model_id_raises_value_error(self):
        """지원하지 않는 model_id에 대해 ValueError가 발생해야 합니다."""
        mgr = LlamaManager()
        with pytest.raises(ValueError, match="is not supported"):
            mgr.load_model("invalid-model-xyz")


class TestTokenValidation:
    """HF_TOKEN 환경변수 검증."""

    def test_get_hf_token_returns_string(self):
        """정상적으로 .env에서 토큰이 로드되면 문자열이 반환되어야 합니다."""
        # .env 파일에 토큰이 설정되어 있으므로 정상 반환
        token = get_hf_token()
        assert isinstance(token, str)
        assert token.startswith("hf_")

    def test_get_hf_token_fails_when_missing(self, monkeypatch):
        """HF_TOKEN이 없으면 EnvironmentError가 발생해야 합니다."""
        monkeypatch.delenv("HF_TOKEN", raising=False)
        with pytest.raises(EnvironmentError, match="HF_TOKEN"):
            get_hf_token()
