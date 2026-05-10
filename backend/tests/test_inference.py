from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_predict_endpoint():
    response = client.post("/predict", json={"target_error": 0.1})
    assert response.status_code == 200
    data = response.json()
    assert "spacings" in data
    assert "positions" in data
    assert len(data["spacings"]) == 3
    assert len(data["positions"]) == 4

def test_verify_endpoint():
    response = client.post("/verify", json={
        "spacings": [0.05, 0.05, 0.05],
        "target_error": 0.5
    })
    assert response.status_code == 200
    data = response.json()
    assert "achieved_error" in data
    assert "crlb_error" in data
    assert "acceptable" in data

def test_chat_endpoint():
    response = client.post("/chat", json={"message": "Design an array with 0.15 degrees error"})
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "data" in data
    assert "spacings" in data["data"]
