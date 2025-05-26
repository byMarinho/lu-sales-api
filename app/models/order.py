from sqlalchemy import Column, Date, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from app.core.database import Base

OrderProduct = Table(
    "order_product",
    Base.metadata,
    Column("order_id", Integer, ForeignKey("orders.id")),
    Column("product_id", Integer, ForeignKey("products.id")),
    Column("quantity", Integer, nullable=False),
)


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    previous_status = Column(String, nullable=False)
    new_status = Column(String, nullable=False)
    order = relationship("Order", back_populates="status_history")

    def __repr__(self):
        return f"<OrderStatusHistory(id={self.id}, order_id={self.order_id}, status={self.new_status})>"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    status = Column(String, default="pending", nullable=False)
    created_at = Column(Date, nullable=False)
    products = relationship(
        "Product",
        secondary=OrderProduct,
        back_populates="orders",
        lazy="dynamic",
    )

    status_history = relationship(
        "OrderStatusHistory",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<Order(id={self.id}, client_id={self.client_id}, date={self.created_at})>"
