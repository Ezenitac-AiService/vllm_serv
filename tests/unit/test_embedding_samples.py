"""tests/unit/test_embedding_samples.py

sample_03_embedding.py 및 openai_03_embedding.py 단일/배치 임베딩 추출 회귀 검증 수트.
"""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "samples")
if SAMPLES_DIR not in sys.path:
    sys.path.insert(0, SAMPLES_DIR)

import sample_03_embedding
import openai_03_embedding


@pytest.fixture(autouse=True)
def mock_embedding_environment():
    """임베딩 SDK 및 httpx 헬스체크 모킹."""
    mock_data1 = MagicMock()
    mock_data1.embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
    mock_data2 = MagicMock()
    mock_data2.embedding = [0.6, 0.7, 0.8, 0.9, 1.0]

    mock_usage = MagicMock()
    mock_usage.prompt_tokens = 20

    mock_emb_response = MagicMock()
    mock_emb_response.data = [mock_data1, mock_data2]
    mock_emb_response.usage = mock_usage

    mock_instance = MagicMock()
    mock_instance.embeddings.create.return_value = mock_emb_response

    with patch("sample_03_embedding.check_server_health", return_value=True), \
         patch("openai_03_embedding.check_server_health", return_value=True), \
         patch("openai_03_embedding.OpenAI", return_value=mock_instance):
        yield mock_instance


def test_sample_03_embedding():
    """sample_03_embedding.py httpx 단일/배치 임베딩 호출 검증."""
    with patch("httpx.Client") as mock_httpx:
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {
            "data": [
                {"embedding": [0.1, 0.2, 0.3]},
                {"embedding": [0.4, 0.5, 0.6]}
            ],
            "usage": {"prompt_tokens": 15}
        }
        mock_client.post.return_value = mock_resp
        mock_httpx.return_value = mock_client
        assert sample_03_embedding.run_embedding_sample() is True


def test_openai_03_embedding():
    """openai_03_embedding.py SDK 단일/배치 임베딩 호출 검증."""
    assert openai_03_embedding.run_embedding_sample() is True
