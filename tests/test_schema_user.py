import pytest
from app.models.user import AccessLevel
from app.schemas.user import UserCreate

def test_user_create_schema():
    user = UserCreate(
        name="Teste",
        email="teste@exemplo.com",
        phone="11999999999",
        access_level=AccessLevel.seller,
        password="12345678"
    )
    assert user.name == "Teste"
    assert user.access_level.value == AccessLevel.seller.value
    assert user.password == "12345678"
