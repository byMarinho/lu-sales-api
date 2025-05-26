import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def test_register_and_login():
    # Registro com e-mail único
    unique_email = f"testuser_{uuid.uuid4()}@example.com"
    user_data = {
        "name": "Test User",
        "email": unique_email,
        "phone": "11999999999",
        "access_level": "seller",
        "password": "12345678"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200, f"Status: {response.status_code}, Body: {response.text}"
    data = response.json()
    assert "access_token" in data, f"access_token não encontrado. Body: {response.text}"
    assert data["access_token"], f"access_token vazio. Body: {response.text}"
    token = data["access_token"]

    # Login
    login_data = {"email": user_data["email"], "password": user_data["password"]}
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200, f"Status: {response.status_code}, Body: {response.text}"
    data = response.json()
    assert "access_token" in data, f"access_token não encontrado no login. Body: {response.text}"
    assert data["access_token"], f"access_token vazio no login. Body: {response.text}"

    # Refresh token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/auth/refresh-token", headers=headers)
    assert response.status_code == 200, f"Status: {response.status_code}, Body: {response.text}"
    data = response.json()
    assert "access_token" in data, f"access_token não encontrado no refresh. Body: {response.text}"
    assert data["access_token"], f"access_token vazio no refresh. Body: {response.text}"

    # Logout
    response = client.post("/api/v1/auth/logout", headers=headers)
    assert response.status_code == 200, f"Status: {response.status_code}, Body: {response.text}"
    data = response.json()
    assert "message" in data, f"Campo 'message' não encontrado no logout. Body: {response.text}"
    assert data["message"] == "Logout realizado com sucesso.", f"Mensagem inesperada no logout: {data['message']}"
