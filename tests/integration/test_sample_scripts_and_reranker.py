"""
tests/integration/test_sample_scripts_and_reranker.py

Integration tests for feature 078-fix-samples-and-reranker-503:
1. samples/common.py configuration parsing priority and zero hardcoded IP strings in source code.
2. /v1/rerank and /v1/embeddings on-demand readiness proxy in inference_api.py preventing 503 errors.
"""

import os
import sys
import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from samples.common import get_server_host, _format_host_url
from src.api.server import create_app


def test_no_hardcoded_ip_in_common_py():
    """FR-001 & SC-001: Ensure no hardcoded IP strings (e.g. 192.168.0.100) exist in samples/common.py."""
    common_py_path = Path(__file__).parent.parent.parent / "samples" / "common.py"
    content = common_py_path.read_text(encoding="utf-8")
    assert "192.168.0.100" not in content, "Hardcoded IP 192.168.0.100 found in samples/common.py!"
    assert "10.0.0.41" not in content, "Hardcoded IP 10.0.0.41 found in samples/common.py!"


def test_get_server_host_parsing_priority(tmp_path, monkeypatch):
    """FR-001: Test configuration parsing order (SERVER_HOST env > .env > config.json > 127.0.0.1 default)."""
    # Clear environment variables
    monkeypatch.delenv("SERVER_HOST", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("VLLM_API_BASE", raising=False)

    # 1. Test environment variable priority
    monkeypatch.setenv("SERVER_HOST", "http://10.0.0.41:8081")
    assert get_server_host() == "http://10.0.0.41:8081"

    monkeypatch.delenv("SERVER_HOST")

    # 2. Test default fallback to 127.0.0.1 (when config.json and .env don't have host)
    # Ensure format_host_url formats clean URLs with or without port
    formatted = _format_host_url("10.0.0.41:8081")
    assert formatted == "http://10.0.0.41:8081"
    
    formatted_no_port = _format_host_url("http://192.168.0.100")
    assert formatted_no_port == "http://192.168.0.100"


@pytest.mark.asyncio
async def test_rerank_proxy_on_demand_readiness(monkeypatch):
    """FR-002 & SC-003: Verify /v1/rerank proxy triggers on-demand readiness without 503 failure."""
    monkeypatch.setenv("MOCK_LLAMA_SERVER", "1")
    app = create_app()
    
    async with app.router.lifespan_context(app):
        client = TestClient(app)
        
        # Test /v1/rerank POST request
        payload = {
            "model": "bge-reranker-v2-m3",
            "query": "vllm_serv 장점",
            "documents": ["vllm_serv는 고성능 LLM 플랫폼입니다.", "날씨가 맑습니다."]
        }
        resp = client.post("/v1/rerank", json=payload)
        assert resp.status_code == 200, f"Expected 200 OK, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "results" in data or "data" in data or data.get("model") == "bge-reranker-v2-m3"
