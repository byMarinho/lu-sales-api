from datetime import date
from typing import Optional

from pydantic import BaseModel


class ProductBase(BaseModel):
    description: str
    price: float
    barcode: str
    section: str
    stock: int
    expiration_date: Optional[date]
    image: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class ProductOut(ProductBase):
    id: int

    class Config:
        from_attributes = True
