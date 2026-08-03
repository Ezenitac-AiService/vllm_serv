"""tests/unit/test_rerank_structured_samples.py

sample_04~06 및 openai_04~06 Reranker 및 단일/배치 구조화 응답 샘플 회귀 검증 수트.
"""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "samples")
if SAMPLES_DIR not in sys.path:
    sys.path.insert(0, SAMPLES_DIR)

import sample_04_reranking
import openai_04_reranking
import sample_05_structured_output
import openai_05_structured_output
import sample_06_structured_output_batch
import openai_06_structured_output_batch


@pytest.fixture(autouse=True)
def mock_rerank_structured_environment():
    """Reranker 및 Structured Output SDK 모킹."""
    mock_post_resp = MagicMock()
    mock_post_resp.get.return_value = [{"index": 0, "relevance_score": 0.95}]
    mock_post_resp.json.return_value = {"results": [{"index": 0, "relevance_score": 0.95}]}

    json_str = '{"results": [{"speaker": "개미왕", "category": "매수/매도 의도", "sentiment": "매수/긍정", "target": "삼성전자", "sentence": "삼전 급등 줍줍", "refined_sentence": "삼성전자 주식 매수"}]}'

    mock_choice = MagicMock()
    mock_choice.message.content = json_str
    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]

    mock_instance = MagicMock()
    mock_instance.post.return_value = mock_post_resp
    mock_instance.chat.completions.create.return_value = mock_completion

    with patch("sample_04_reranking.check_server_health", return_value=True), \
         patch("openai_04_reranking.check_server_health", return_value=True), \
         patch("sample_05_structured_output.check_server_health", return_value=True), \
         patch("openai_05_structured_output.check_server_health", return_value=True), \
         patch("sample_06_structured_output_batch.check_server_health", return_value=True), \
         patch("openai_06_structured_output_batch.check_server_health", return_value=True), \
         patch("openai_04_reranking.OpenAI", return_value=mock_instance), \
         patch("openai_05_structured_output.OpenAI", return_value=mock_instance), \
         patch("openai_06_structured_output_batch.OpenAI", return_value=mock_instance):
        yield mock_instance


def test_sample_04_reranking():
    with patch("httpx.Client") as mock_httpx:
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"results": [{"index": 0, "relevance_score": 0.98}]}
        mock_client.post.return_value = mock_resp
        mock_httpx.return_value = mock_client
        assert sample_04_reranking.run_reranking_sample() is True


def test_openai_04_reranking():
    assert openai_04_reranking.run_reranking_sample() is True


def test_sample_05_structured_output():
    json_str = '{"results": [{"speaker": "개미왕", "category": "매수/매도 의도", "sentiment": "매수/긍정", "target": "삼성전자", "sentence": "삼전 급등 줍줍", "refined_sentence": "삼성전자 주식 매수"}]}'
    with patch("httpx.Client") as mock_httpx:
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"choices": [{"message": {"content": json_str}}]}
        mock_client.post.return_value = mock_resp
        mock_httpx.return_value = mock_client
        assert sample_05_structured_output.run_structured_output_sample() is True


def test_openai_05_structured_output():
    assert openai_05_structured_output.run_structured_output_sample() is True


def test_sample_06_structured_output_batch():
    json_str = '{"results": [{"speaker": "개미왕", "category": "매수/매도 의도", "sentiment": "매수/긍정", "target": "삼성전자", "sentence": "삼전 급등 줍줍", "refined_sentence": "삼성전자 주식 매수"}]}'
    with patch("httpx.Client") as mock_httpx:
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"choices": [{"message": {"content": json_str}}]}
        mock_client.post.return_value = mock_resp
        mock_httpx.return_value = mock_client
        assert sample_06_structured_output_batch.run_structured_output_batch_sample() is True


def test_openai_06_structured_output_batch():
    assert openai_06_structured_output_batch.run_structured_output_batch_sample() is True
