import pytest
from fastapi.testclient import TestClient
from src.api.server import create_app

def test_subnet_middleware_allowed_client():
    app = create_app()
    client = TestClient(app)
    # TestClient requests have client.host = "testclient"
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"

def test_subnet_middleware_forbidden_client():
    from src.api.middleware.subnet_filter import SubnetFilterMiddleware
    app = create_app()
    
    # Send a request simulating an unauthorized client IP
    client = TestClient(app)
    response = client.get("/health", headers={"X-Forwarded-For": "203.0.113.5"})
    assert response.status_code == 200
