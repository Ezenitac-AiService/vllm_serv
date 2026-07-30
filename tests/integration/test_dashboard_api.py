import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.api.main import app

client = TestClient(app)

def test_capabilities():
    response = client.get("/dashboard/api/capabilities")
    assert response.status_code == 200
    data = response.json()
    assert "vram_total" in data
    assert "limits" in data

def test_status():
    response = client.get("/dashboard/api/status")
    assert response.status_code == 200
    data = response.json()
    assert "state" in data
    assert data["state"] == "UNLOADED"

@patch('src.core.llama_manager.LlamaManager._start_server_subprocess')
def test_apply_and_unload(mock_start):
    # Mock to do nothing
    mock_start.return_value = None

    headers = {"X-Admin-Secret": "aiservice"}
    payload = {"model_id": "test-model", "n_ctx": 1024}
    response = client.post("/dashboard/api/apply", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    response = client.post("/dashboard/api/unload", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
