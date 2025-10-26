"""
Tests para el API
"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root():
    """Test del endpoint raíz"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    """Test del health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_endpoint():
    """Test del endpoint de chat"""
    response = client.post(
        "/chat",
        json={"message": "Hola", "conversation_id": "test-123"}
    )
    assert response.status_code == 200
    assert "response" in response.json()
    assert "conversation_id" in response.json()


def test_model_status():
    """Test del estado del modelo"""
    response = client.get("/model/status")
    assert response.status_code == 200
    assert "model_loaded" in response.json()
