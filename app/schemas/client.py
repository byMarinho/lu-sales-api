from pydantic import BaseModel, EmailStr, constr
from typing_extensions import Annotated


class ClientBase(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None
    cpf: Annotated[str, constr(min_length=11, max_length=11)] | None = None
    address: str | None = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(ClientBase):
    pass


class ClientOut(ClientBase):
    id: int

    class Config:
        from_attributes = True
