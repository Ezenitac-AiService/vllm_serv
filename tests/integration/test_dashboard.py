import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.api.main import app

client = TestClient(app)

@patch('src.core.llama_manager.LlamaManager.unload_model')
def test_inference_503(mock_unload):
    # Make sure we start in UNLOADED state
    response = client.post("/dashboard/api/unload")
    
    # Try to access /v1/chat/completions
    response = client.post("/v1/chat/completions", json={"prompt": "test"})
    assert response.status_code == 503
    assert "Retry-After" in response.headers
    assert response.headers["Retry-After"] == "10"
