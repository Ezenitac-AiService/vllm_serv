import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

# Mock the manager before importing the app
with patch('src.core.llama_manager.LlamaManager.generate') as mock_generate, \
     patch('src.core.llama_manager.LlamaManager.load_model') as mock_load:
     
    # Setup mock returns
    mock_generate.return_value = {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gemma4-12b",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Hi there!"
            },
            "finish_reason": "stop"
        }]
    }
    mock_load.return_value = {"status": "success", "message": "Loaded"}
    
    # Now import app
    from src.api.server import app

client = TestClient(app)

def test_chat_completions():
    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "gemma4-12b",
            "messages": [{"role": "user", "content": "Hello!"}]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "choices" in data
    assert data["choices"][0]["message"]["content"] == "Hi there!"

def test_chat_completions_error_handling():
    with patch('src.api.routes.manager.generate', side_effect=Exception("CUDA out of memory")):
        response = client.post(
            "/v1/chat/completions",
            json={
                "model": "gemma4-12b",
                "messages": [{"role": "user", "content": "Hello!"}]
            }
        )
        assert response.status_code == 503
        assert "out of memory" in response.json()["detail"].lower()
