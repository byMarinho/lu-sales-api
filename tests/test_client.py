import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import get_db
import uuid

client = TestClient(app)

def get_auth_header():
    unique_email = f"clienteteste_{uuid.uuid4()}@example.com"
    user_data = {
        "name": "Cliente Teste",
        "email": unique_email,
        "phone": "11999999999",
        "access_level": "seller",
        "password": "12345678"
    }
    client.post("/api/v1/auth/register", json=user_data)
    login_data = {"email": user_data["email"], "password": user_data["password"]}
    response = client.post("/api/v1/auth/login", json=login_data)
    return {"Authorization": f"Bearer {response.json()['access_token']}"}

def test_create_and_list_client():
    headers = get_auth_header()
    unique_email = f"cliente1_{uuid.uuid4()}@example.com"
    unique_cpf = str(uuid.uuid4().int)[:11]
    client_data = {
        "name": "Cliente 1",
        "email": unique_email,
        "phone": "11999999997",
        "cpf": unique_cpf,
        "address": "Rua Teste, 123"
    }
    response = client.post("/api/v1/clients/", json=client_data, headers=headers)
    assert response.status_code == 200, f"Status: {response.status_code}, Body: {response.text}"
    client_id = response.json()["id"]

    # Buscar apenas pelo e-mail único criado
    response = client.get(f"/api/v1/clients/?email={unique_email}", headers=headers)
    print("LIST CLIENTS RESPONSE:", response.json())
    assert response.status_code == 200
    clients = response.json()
    assert any(c["id"] == client_id for c in clients), "Cliente criado não encontrado na listagem"

    response = client.get(f"/api/v1/clients/{client_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == client_data["email"]

    # Atualizar cliente
    update_data = {"name": "Cliente 1 Atualizado", "email": unique_email, "phone": "11999999997", "cpf": unique_cpf, "address": "Rua Teste, 123"}
    response = client.put(f"/api/v1/clients/{client_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Cliente 1 Atualizado"

    # Deletar cliente
    response = client.delete(f"/api/v1/clients/{client_id}", headers=headers)
    assert response.status_code == 204
