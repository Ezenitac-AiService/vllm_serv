"""tests/unit/test_sample_scripts.py

samples/ 디렉터리의 12종 샘플 스크립트 실행 및 서빙 포트 연동 회귀 검증 수트.
"""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# samples 디렉터리를 sys.path에 포함
SAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "samples")
if SAMPLES_DIR not in sys.path:
    sys.path.insert(0, SAMPLES_DIR)

from common import check_server_health, get_server_host, load_sample_config
import sample_01_chat
import sample_02_model_params
import sample_03_embedding
import sample_04_reranking
import sample_05_structured_output
import sample_06_structured_output_batch
import openai_01_chat
import openai_02_model_params
import openai_03_embedding
import openai_04_reranking
import openai_05_structured_output
import openai_06_structured_output_batch


@pytest.fixture(autouse=True)
def mock_all_samples_environment():
    """모든 12개 샘플 스크립트 테스트가 200 OK 응답을 시뮬레이션하도록 모킹."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status.return_value = None
    json_str = '{"results": [{"speaker": "개미왕", "category": "매수/매도 의도", "sentiment": "매수/긍정", "target": "삼성전자", "sentence": "삼전 급등 줍줍", "refined_sentence": "삼성전자 주식 매수"}]}'
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": json_str}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        "data": [{"embedding": [0.1, 0.2, 0.3]}, {"embedding": [0.4, 0.5, 0.6]}],
        "results": [{"index": 0, "relevance_score": 0.95}],
    }

    mock_choice = MagicMock()
    mock_choice.message.content = json_str
    mock_choice.finish_reason = "stop"

    mock_usage = MagicMock()
    mock_usage.prompt_tokens = 10
    mock_usage.completion_tokens = 5
    mock_usage.total_tokens = 15

    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]
    mock_completion.usage = mock_usage

    mock_emb_data = MagicMock()
    mock_emb_data.embedding = [0.1, 0.2, 0.3]
    mock_emb_resp = MagicMock()
    mock_emb_resp.data = [mock_emb_data, mock_emb_data]
    mock_emb_resp.usage = mock_usage

    mock_post_resp = MagicMock()
    mock_post_resp.get.return_value = [{"index": 0, "relevance_score": 0.95}]
    mock_post_resp.json.return_value = {"results": [{"index": 0, "relevance_score": 0.95}]}

    mock_openai_inst = MagicMock()
    mock_openai_inst.chat.completions.create.return_value = mock_completion
    mock_openai_inst.embeddings.create.return_value = mock_emb_resp
    mock_openai_inst.post.return_value = mock_post_resp

    with patch("httpx.get", return_value=mock_resp), \
         patch("httpx.Client") as mock_client_cls, \
         patch("common.check_server_health", return_value=True), \
         patch("openai_01_chat.check_server_health", return_value=True), \
         patch("openai_02_model_params.check_server_health", return_value=True), \
         patch("openai_03_embedding.check_server_health", return_value=True), \
         patch("openai_04_reranking.check_server_health", return_value=True), \
         patch("openai_05_structured_output.check_server_health", return_value=True), \
         patch("openai_06_structured_output_batch.check_server_health", return_value=True), \
         patch("openai_01_chat.OpenAI", return_value=mock_openai_inst), \
         patch("openai_02_model_params.OpenAI", return_value=mock_openai_inst), \
         patch("openai_03_embedding.OpenAI", return_value=mock_openai_inst), \
         patch("openai_04_reranking.OpenAI", return_value=mock_openai_inst), \
         patch("openai_05_structured_output.OpenAI", return_value=mock_openai_inst), \
         patch("openai_06_structured_output_batch.OpenAI", return_value=mock_openai_inst):
        
        instance = MagicMock()
        instance.__enter__.return_value = instance
        instance.post.return_value = mock_resp
        instance.get.return_value = mock_resp
        mock_client_cls.return_value = instance
        yield mock_resp


def test_common_healthcheck():
    host = get_server_host()
    assert host.startswith("http://") or host.startswith("https://")
    is_healthy = check_server_health(host, 8081, "Test LLM Server")
    assert is_healthy is True


def test_common_load_config():
    config = load_sample_config()
    assert "server_host" in config
    assert "main_port" in config
    assert "default_model" in config


def test_all_12_sample_scripts():
    assert sample_01_chat.run_chat_sample() is True
    assert sample_02_model_params.run_model_params_sample() is True
    assert sample_03_embedding.run_embedding_sample() is True
    assert sample_04_reranking.run_reranking_sample() is True
    assert sample_05_structured_output.run_structured_output_sample() is True
    assert sample_06_structured_output_batch.run_structured_output_batch_sample() is True
    assert openai_01_chat.run_chat_sample() is True
    assert openai_02_model_params.run_model_params_sample() is True
    assert openai_03_embedding.run_embedding_sample() is True
    assert openai_04_reranking.run_reranking_sample() is True
    assert openai_05_structured_output.run_structured_output_sample() is True
    assert openai_06_structured_output_batch.run_structured_output_batch_sample() is True
