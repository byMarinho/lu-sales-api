import pytest
from app.schemas.order import OrderCreate, OrderProduct

def test_order_create_schema():
    order = OrderCreate(
        client_id=1,
        status="pending",
        created_at="2025-05-25",
        products=[OrderProduct(product_id=1, quantity=2)]
    )
    assert order.client_id == 1
    assert order.status == "pending"
    assert order.products[0].product_id == 1
    assert order.products[0].quantity == 2
