import pytest
from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy.orm import Session
from app.core.database import get_db
import uuid

client = TestClient(app)

def get_auth_header():
    unique_email = f"produtoteste_{uuid.uuid4()}@example.com"
    user_data = {
        "name": "Produto Teste",
        "email": unique_email,
        "phone": "11999999999",
        "access_level": "seller",
        "password": "12345678"
    }
    client.post("/api/v1/auth/register", json=user_data)
    login_data = {"email": unique_email, "password": user_data["password"]}
    response = client.post("/api/v1/auth/login", json=login_data)
    return {"Authorization": f"Bearer {response.json()['access_token']}"}

def test_create_and_list_product():
    headers = get_auth_header()
    unique_description = f"Produto 1 {uuid.uuid4()}"
    unique_barcode = str(uuid.uuid4().int)[:13]
    product_data = {
        "description": unique_description,
        "price": 10.5,
        "barcode": unique_barcode,
        "section": "Roupas",
        "stock": 5,
        "expiration_date": "2025-12-31",
        "image": None
    }
    response = client.post("/api/v1/products/", json=product_data, headers=headers)
    assert response.status_code == 200, f"Status: {response.status_code}, Body: {response.text}"
    product_id = response.json()["id"]

    # Buscar apenas pelo description único criado
    response = client.get(f"/api/v1/products/?description={unique_description}", headers=headers)
    print("LIST PRODUCTS RESPONSE:", response.json())
    assert response.status_code == 200, f"Status: {response.status_code}, Body: {response.text}"
    products = response.json()
    assert any(p["id"] == product_id for p in products), "Produto criado não encontrado na listagem"

    response = client.get(f"/api/v1/products/{product_id}", headers=headers)
    assert response.status_code == 200, f"Status: {response.status_code}, Body: {response.text}"
    assert response.json()["description"] == product_data["description"]

    # Atualizar produto
    update_data = product_data.copy()
    update_data["description"] = "Produto 1 Atualizado"
    response = client.put(f"/api/v1/products/{product_id}", json=update_data, headers=headers)
    assert response.status_code == 200, f"Status: {response.status_code}, Body: {response.text}"
    assert response.json()["description"] == "Produto 1 Atualizado"

    # Deletar produto
    response = client.delete(f"/api/v1/products/{product_id}", headers=headers)
    assert response.status_code == 204
