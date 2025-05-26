import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_whatsapp():
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "SENT"}
    
    with patch('requests.post', return_value=mock_response) as mock:
        yield mock

def get_auth_header():
    user_data = {
        "name": "User Integration",
        "email": "integration@example.com",
        "phone": "11999999990",
        "access_level": "seller",
        "password": "12345678"
    }
    client.post("/api/v1/auth/register", json=user_data)
    login_data = {"email": user_data["email"], "password": user_data["password"]}
    response = client.post("/api/v1/auth/login", json=login_data)
    return {"Authorization": f"Bearer {response.json()['access_token']}"}

def test_order_integration_flow(mock_whatsapp):
    headers = get_auth_header()
    # Criar cliente
    unique_email = f"clientepedido_int_{uuid.uuid4()}@example.com"
    unique_cpf = str(uuid.uuid4().int)[:11]
    client_data = {
        "name": "Cliente Pedido Int",
        "email": unique_email,
        "phone": "11999999991",
        "cpf": unique_cpf,
        "address": "Rua Integração, 123"
    }
    response = client.post("/api/v1/clients/", json=client_data, headers=headers)
    assert response.status_code == 200, f"Status: {response.status_code}, Body: {response.text}"
    client_id = response.json()["id"]
    # Criar produto
    unique_description = f"Produto Int {uuid.uuid4()}"
    unique_barcode = str(uuid.uuid4().int)[:13]
    product_data = {
        "description": unique_description,
        "price": 30.0,
        "barcode": unique_barcode,
        "section": "Roupas",
        "stock": 20,
        "expiration_date": "2025-12-31",
        "image": None
    }
    response = client.post("/api/v1/products/", json=product_data, headers=headers)
    assert response.status_code == 200, f"Status: {response.status_code}, Body: {response.text}"
    product_id = response.json()["id"]
    # Criar pedido
    order_data = {
        "client_id": client_id,
        "status": "pending",
        "created_at": "2025-05-25",
        "products": [
            {"product_id": product_id, "quantity": 2}
        ]
    }
    response = client.post("/api/v1/orders/", json=order_data, headers=headers)
    assert response.status_code == 201
    order_id = response.json()["id"]
    
    # Verificar se o WhatsApp foi chamado
    assert mock_whatsapp.called
    
    # Listar pedidos apenas do cliente criado
    response = client.get(f"/api/v1/orders/?client_id={client_id}", headers=headers)
    assert response.status_code == 200
    assert any(o["id"] == order_id for o in response.json()), "Pedido criado não encontrado na listagem"
    # Buscar pedido
    response = client.get(f"/api/v1/orders/{order_id}", headers=headers)
    assert response.status_code == 200
    # Atualizar pedido
    update_data = {
        "client_id": client_id,
        "status": "pending",
        "created_at": "2025-05-25",
        "products": [
            {"product_id": product_id, "quantity": 5}
        ]
    }
    response = client.put(f"/api/v1/orders/{order_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["products"][0]["quantity"] == 5
    # Atualizar status
    response = client.put(f"/api/v1/orders/{order_id}/status", json={"status": "processing", "client_id": client_id, "created_at": "2025-05-25"}, headers=headers)
    assert response.status_code == 200
    # Deletar pedido
    response = client.delete(f"/api/v1/orders/{order_id}", headers=headers)
    assert response.status_code == 204
