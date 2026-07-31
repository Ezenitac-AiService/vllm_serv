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
from sample_02_model_params import run_params_sample
from sample_03_embedding import run_embedding_sample
from sample_04_reranking import run_reranking_sample
from sample_05_structured_output import run_structured_output_sample


def test_common_healthcheck():
    """samples/common.py 동적 IP 헬스체크 및 get_server_host() 테스트."""
    host = get_server_host()
    assert host.startswith("http://") or host.startswith("https://")
    # 8081 포트 동적 IP 수신 확인
    is_healthy = check_server_health(host, 8081, "Test LLM Server")
    assert is_healthy is True


def test_sample_01_chat():
    """sample_01_chat.py 대화 호출 실행 테스트."""
    success = run_chat_sample()
    assert success is True


def test_sample_02_model_params():
    """sample_02_model_params.py 파라미터 제어 실행 테스트."""
    success = run_params_sample()
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
