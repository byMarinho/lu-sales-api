from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=False)
    cpf = Column(String, unique=True, nullable=False, index=True)
    address = Column(String, nullable=False)

    def __repr__(self):
        return f"<Client(id={self.id}, name={self.name}, email={self.email})>"
