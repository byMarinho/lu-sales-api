import pytest
from app.schemas.client import ClientCreate

def test_client_create_schema():
    client = ClientCreate(
        name="Cliente Teste",
        email="cliente@exemplo.com",
        phone="11999999999",
        cpf="12345678901",
        address="Rua Teste, 123"
    )
    assert client.name == "Cliente Teste"
    assert client.cpf == "12345678901"
    assert client.address == "Rua Teste, 123"
