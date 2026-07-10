import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

# Mock the manager before importing the app
with patch('src.core.llama_manager.LlamaManager.load_model') as mock_load:
    mock_load.return_value = {
        "status": "success",
        "message": "Model switched to gemma4-4b",
        "load_time_sec": 1.23
    }
    from src.api.server import app

client = TestClient(app)

def test_model_switch_success():
    response = client.post(
        "/api/models/switch",
        json={"model_id": "gemma4-4b"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["model_id"] == "gemma4-4b" or "switched to gemma4-4b" in data["message"]

def test_model_switch_invalid_model():
    with patch('src.api.routes.manager.load_model', side_effect=ValueError("Model ID 'invalid' is not supported.")):
        response = client.post(
            "/api/models/switch",
            json={"model_id": "invalid"}
        )
        assert response.status_code == 400
        assert "not supported" in response.json()["detail"]

def test_model_switch_not_found():
    with patch('src.api.routes.manager.load_model', side_effect=FileNotFoundError("Model file not found")):
        response = client.post(
            "/api/models/switch",
            json={"model_id": "gemma4-12b"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
