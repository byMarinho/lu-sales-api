from sqlalchemy import Column, Date, Float, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    barcode = Column(String, unique=True, nullable=False, index=True)
    section = Column(String, nullable=False)
    stock = Column(Integer, default=0, nullable=False)
    expiration_date = Column(Date, nullable=False)
    image = Column(String, nullable=True)

    orders = relationship(
        "Order",
        secondary="order_product",
        back_populates="products",
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.description}, price={self.price}), stock={self.stock})>"
