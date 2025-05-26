from sqlalchemy import Boolean, Column, Enum, Integer, String
import enum
from app.core.database import Base

class AccessLevel(enum.Enum):
    admin = "admin"
    user = "user"
    seller = "seller"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=True)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    access_level = Column(Enum(AccessLevel), default=AccessLevel.user)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.name}, email={self.email}, access_level={self.access_level})>"
