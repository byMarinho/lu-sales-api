from enum import Enum

from pydantic import BaseModel, EmailStr, constr
from typing_extensions import Annotated


class AccessLevel(str, Enum):
    admin = "admin"
    user = "user"
    seller = "seller"


class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None
    access_level: AccessLevel = AccessLevel.user


class UserCreate(UserBase):
    password: Annotated[str, constr(min_length=8)]

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Admin",
                "email": "admin@exemplo.com",
                "phone": "11999999999",
                "access_level": "admin",
                "password": "12345678"
            }
        }


class UserUpdate(UserBase):
    password: Annotated[str, constr(min_length=8)] | None = None
    is_active: bool | None = None


class UserOut(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
