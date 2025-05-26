import pytest
from app.schemas.product import ProductCreate

def test_product_create_schema():
    product = ProductCreate(
        description="Produto Teste",
        price=10.0,
        barcode="1234567890000",
        section="Roupas",
        stock=5,
        expiration_date="2025-12-31",
        image=None
    )
    assert product.description == "Produto Teste"
    assert product.price == 10.0
    assert product.section == "Roupas"
