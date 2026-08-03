"""tests/unit/test_sample_scripts.py

samples/ 디렉터리의 5종 샘플 스크립트 실행 및 서빙 포트 연동 회귀 검증 수트.
"""

import sys
import os
import pytest

# samples 디렉터리를 sys.path에 포함
SAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "samples")
if SAMPLES_DIR not in sys.path:
    sys.path.insert(0, SAMPLES_DIR)

from common import check_server_health, get_server_host
from sample_01_chat import run_chat_sample
from sample_02_model_params import run_model_params_sample
from sample_03_embedding import run_embedding_sample
from sample_04_reranking import run_reranking_sample
from sample_05_structured_output import run_structured_output_sample


from unittest.mock import patch, MagicMock

@pytest.fixture(autouse=True)
def mock_httpx_response():
    """모든 샘플 스크립트 테스트가 200 OK 응답을 시뮬레이션하도록 httpx 모킹."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status.return_value = None
    json_str = '{"results": [{"speaker": "개미왕", "category": "매수/매도 의도", "sentiment": "매수/긍정", "target": "삼성전자", "sentence": "삼전 급등 줍줍", "refined_sentence": "삼성전자 주식 매수"}]}'
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": json_str}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        "data": [{"embedding": [0.1, 0.2, 0.3]}],
        "results": [{"index": 0, "relevance_score": 0.95}],
    }
    with patch("httpx.get", return_value=mock_resp), \
         patch("httpx.Client") as mock_client_cls:
        instance = MagicMock()
        instance.__enter__.return_value = instance
        instance.post.return_value = mock_resp
        instance.get.return_value = mock_resp
        mock_client_cls.return_value = instance
        yield mock_resp


def test_common_healthcheck():
    """samples/common.py get_server_host 및 check_server_health 테스트."""
    host = get_server_host()
    assert host.startswith("http://") or host.startswith("https://")
    is_healthy = check_server_health(host, 8081, "Test LLM Server")
    assert is_healthy is True


def test_get_server_host_config_json(tmp_path, monkeypatch):
    """config.json 파일 파싱 테스트."""
    monkeypatch.delenv("SERVER_HOST", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("VLLM_API_BASE", raising=False)
    monkeypatch.setenv("SAMPLES_DIR", str(tmp_path))

    config_json = tmp_path / "config.json"
    config_json.write_text('{"server_host": "http://192.168.0.150"}', encoding="utf-8")

    host = get_server_host()
    assert host == "http://192.168.0.150"


def test_sample_01_chat():
    """sample_01_chat.py 대화 호출 실행 테스트."""
    success = run_chat_sample()
    assert success is True


def test_sample_02_model_params():
    """sample_02_model_params.py 파라미터 제어 실행 테스트."""
    success = run_model_params_sample()
    assert success is True


def test_sample_03_embedding():
    """sample_03_embedding.py BGE M3 임베딩 모델 호출 테스트."""
    success = run_embedding_sample()
    assert success is True


def test_sample_04_reranking():
    """sample_04_reranking.py BGE Reranker v2 M3 호출 테스트."""
    success = run_reranking_sample()
    assert success is True


def test_sample_05_structured_output():
    """sample_05_structured_output.py Pydantic 구조화 출력 파싱 테스트."""
    success = run_structured_output_sample()
    assert success is True

