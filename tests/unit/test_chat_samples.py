"""tests/unit/test_chat_samples.py

openai_01_chat.py 및 openai_02_model_params.py SDK 대화 및 파라미터 제어 샘플 회귀 검증 수트.
"""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "samples")
if SAMPLES_DIR not in sys.path:
    sys.path.insert(0, SAMPLES_DIR)

import openai_01_chat
import openai_02_model_params


@pytest.fixture(autouse=True)
def mock_openai_environment(monkeypatch):
    """OpenAI SDK 클라이언트 및 서버 헬스체크 모킹."""
    mock_choice = MagicMock()
    mock_choice.message.content = "<think>생각중</think>vllm_serv는 고성능 LLM 서빙 서버입니다."
    mock_choice.finish_reason = "stop"

    mock_usage = MagicMock()
    mock_usage.prompt_tokens = 10
    mock_usage.completion_tokens = 5
    mock_usage.total_tokens = 15

    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]
    mock_completion.usage = mock_usage

    mock_instance = MagicMock()
    mock_instance.chat.completions.create.return_value = mock_completion

    with patch("openai_01_chat.check_server_health", return_value=True), \
         patch("openai_02_model_params.check_server_health", return_value=True), \
         patch("openai_01_chat.OpenAI", return_value=mock_instance), \
         patch("openai_02_model_params.OpenAI", return_value=mock_instance):
        yield mock_instance


def test_openai_01_chat():
    """openai_01_chat.py SDK 대화 샘플 단독 실행 검증."""
    assert openai_01_chat.run_chat_sample() is True


def test_openai_02_model_params():
    """openai_02_model_params.py SDK 파라미터 제어 샘플 단독 실행 검증."""
    assert openai_02_model_params.run_model_params_sample() is True
