import logging
import sentry_sdk
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_seller, get_db
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientOut, ClientUpdate

router = APIRouter(prefix="/clients", tags=["clients"])


@router.post(
    "/",
    response_model=ClientOut,
    responses={
        200: {
            "description": "Cliente criado com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "João Silva",
                        "email": "joao@exemplo.com",
                        "phone": "11999999999",
                        "cpf": "12345678901",
                        "address": "Rua das Flores, 123"
                    }
                }
            },
        },
        400: {"description": "Email ou CPF já existe."},
    },
)
def create_client(
    client_in: ClientCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_seller),
):
    logger = logging.getLogger(__name__)
    try:
        existing_email = db.query(Client).filter(Client.email == client_in.email).first()
        existing_cpf = db.query(Client).filter(Client.cpf == client_in.cpf).first()

        if existing_email or existing_cpf:
            raise HTTPException(
                status_code=400,
                detail="Email or CPF already exists.",
            )

        client = Client(**client_in.model_dump())  # Usando model_dump() em vez de dict()
        db.add(client)
        db.flush()  # Atualiza o ID sem fazer commit
        db.refresh(client)

        return client
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("Erro inesperado ao criar cliente: %s", str(e), exc_info=True)
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Erro interno inesperado")


@router.get(
    "/",
    response_model=List[ClientOut],
    responses={
        200: {
            "description": "Lista de clientes",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "name": "João Silva",
                            "email": "joao@exemplo.com",
                            "phone": "11999999999",
                            "cpf": "12345678901",
                            "address": "Rua das Flores, 123"
                        }
                    ]
                }
            },
        }
    },
)
def list_clients(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_seller),
    name: Optional[str] = None,
    email: Optional[str] = None,
    cpf: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
):
    """
    Lista todos os clientes cadastrados, com filtros opcionais.

    - Permite filtrar por nome, e-mail ou CPF.
    - Retorna os clientes paginados (parâmetros skip e limit).

    **Casos de uso:**
    - Consulta geral de clientes.
    - Busca de clientes para pedidos ou relatórios.
    """
    query = db.query(Client)

    if name:
        query = query.filter(Client.name.ilike(f"%{name}%"))
    if email:
        query = query.filter(Client.email == email)
    if cpf:
        query = query.filter(Client.cpf == cpf)

    return query.offset(skip).limit(limit).all()


@router.get(
    "/{client_id}",
    response_model=ClientOut,
    responses={
        200: {
            "description": "Cliente encontrado",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "João Silva",
                        "email": "joao@exemplo.com",
                        "phone": "11999999999",
                        "cpf": "12345678901",
                        "address": "Rua das Flores, 123"
                    }
                }
            },
        },
        404: {"description": "Client not found"},
    },
)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_seller),
):
    """
    Busca um cliente pelo seu ID.

    - Retorna todos os dados do cliente.
    - Retorna erro 404 caso o cliente não exista.

    **Casos de uso:**
    - Visualização detalhada de um cliente.
    - Consulta para edição ou análise de dados do cliente.
    """
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    return client


@router.put(
    "/{client_id}",
    response_model=ClientOut,
    responses={
        200: {
            "description": "Cliente atualizado",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "João Silva",
                        "email": "joao@exemplo.com",
                        "phone": "11999999999",
                        "cpf": "12345678901",
                        "address": "Rua das Flores, 123"
                    }
                }
            },
        },
        404: {"description": "Client not found"},
    },
)
def update_client(
    client_id: int,
    client_in: ClientUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_seller),
):
    """
    Atualiza os dados de um cliente existente.

    - Permite alterar nome, e-mail, telefone, CPF e endereço.
    - Garante unicidade de e-mail e CPF.
    - Retorna erro 404 caso o cliente não exista.

    **Casos de uso:**
    - Correção de dados cadastrais.
    - Atualização de informações para contato ou entrega.
    """
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    existing_email = db.query(Client).filter(Client.email == client_in.email).first()
    existing_cpf = db.query(Client).filter(Client.cpf == client_in.cpf).first()

    if existing_email and existing_email.id != client_id:
        raise HTTPException(
            status_code=400,
            detail="Email already exists.",
        )
    if existing_cpf and existing_cpf.id != client_id:
        raise HTTPException(
            status_code=400,
            detail="CPF already exists.",
        )

    for field, value in client_in.dict(exclude_unset=True).items():
        setattr(client, field, value)

    db.commit()
    db.refresh(client)

    return client


@router.delete(
    "/{client_id}",
    status_code=204,
    responses={
        204: {"description": "Cliente deletado com sucesso"},
        404: {"description": "Client not found"},
    },
)
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_seller),
):
    """
    Remove um cliente do sistema.

    - Exclui o cliente permanentemente.
    - Retorna erro 404 caso o cliente não exista.

    **Casos de uso:**
    - Exclusão de clientes duplicados ou inativos.
    - Limpeza de base de dados.
    """
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    db.delete(client)
    db.commit()

    return None
