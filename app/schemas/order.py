from datetime import date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class OrderStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    canceled = "canceled"


class OrderProduct(BaseModel):
    product_id: int
    quantity: int


class OrderBase(BaseModel):
    client_id: int
    status: Optional[str] = "pending"
    created_at: date


class OrderCreate(OrderBase):
    products: List[OrderProduct]


class OrderUpdateStatus(OrderBase):
    status: str


class OrderOut(OrderBase):
    id: int
    products: List[OrderProduct]

    class Config:
        from_attributes = True
