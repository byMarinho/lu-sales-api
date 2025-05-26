import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid
from unittest.mock import patch

client = TestClient(app)

def get_auth_header():
    user_data = {
        "name": "Pedido Teste",
        "email": "pedidoteste@example.com",
        "phone": "11999999995",
        "access_level": "seller",
        "password": "12345678"
    }
    client.post("/api/v1/auth/register", json=user_data)
    login_data = {"email": user_data["email"], "password": user_data["password"]}
    response = client.post("/api/v1/auth/login", json=login_data)
    return {"Authorization": f"Bearer {response.json()['access_token']}"}

def create_client_and_product(headers):
    unique_email = f"clientepedido_{uuid.uuid4()}@example.com"
    unique_cpf = str(uuid.uuid4().int)[:11]
    unique_description = f"Produto Pedido {uuid.uuid4()}"
    unique_barcode = str(uuid.uuid4().int)[:13]
    client_data = {
        "name": "Cliente Pedido",
        "email": unique_email,
        "phone": "11999999994",
        "cpf": unique_cpf,
        "address": "Rua Pedido, 123"
    }
    response = client.post("/api/v1/clients/", json=client_data, headers=headers)
    assert response.status_code == 200, f"Status: {response.status_code}, Body: {response.text}"
    client_id = response.json()["id"]
    product_data = {
        "description": unique_description,
        "price": 20.0,
        "barcode": unique_barcode,
        "section": "Roupas",
        "stock": 10,
        "expiration_date": "2025-12-31",
        "image": None
    }
    response = client.post("/api/v1/products/", json=product_data, headers=headers)
    assert response.status_code == 200, f"Status: {response.status_code}, Body: {response.text}"
    product_id = response.json()["id"]
    return client_id, product_id

def test_create_and_update_order():
    headers = get_auth_header()
    client_id, product_id = create_client_and_product(headers)
    order_data = {
        "client_id": client_id,
        "status": "pending",
        "created_at": "2025-05-25",
        "products": [
            {"product_id": product_id, "quantity": 2}
        ]
    }
    # Corrigir o patch para o namespace do endpoint
    with patch("app.api.v1.endpoints.order.send_whatsapp_message"):
        response = client.post("/api/v1/orders/", json=order_data, headers=headers)
    assert response.status_code == 201
    order_id = response.json()["id"]

    response = client.get(f"/api/v1/orders/{order_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["client_id"] == client_id

    # Atualizar pedido (trocar cliente e quantidade)
    new_unique_email = f"clientenovo_{uuid.uuid4()}@example.com"
    new_unique_cpf = str(uuid.uuid4().int)[:11]
    new_client_data = {
        "name": "Cliente Novo",
        "email": new_unique_email,
        "phone": "5511999999993",
        "cpf": new_unique_cpf,
        "address": "Rua Nova, 456"
    }
    response = client.post("/api/v1/clients/", json=new_client_data, headers=headers)
    new_client_id = response.json()["id"]
    update_data = {
        "client_id": new_client_id,
        "status": "pending",
        "created_at": "2025-05-25",
        "products": [
            {"product_id": product_id, "quantity": 3}
        ]
    }
    response = client.put(f"/api/v1/orders/{order_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["client_id"] == new_client_id
    assert response.json()["products"][0]["quantity"] == 3

    # Atualizar status do pedido
    status_data = {"client_id": new_client_id, "status": "processing", "created_at": "2025-05-25"}
    with patch("app.integrations.whatsapp.whatsapp.send_whatsapp_message"):
        response = client.put(f"/api/v1/orders/{order_id}/status", json={"status": "processing", "client_id": new_client_id, "created_at": "2025-05-25"}, headers=headers)
    assert response.status_code == 200
    assert "Order status updated successfully" in response.json()["message"]

    # Deletar pedido
    response = client.delete(f"/api/v1/orders/{order_id}", headers=headers)
    assert response.status_code == 204
