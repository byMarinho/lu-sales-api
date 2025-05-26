from typing import List, Optional
import logging
import sentry_sdk

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_seller, get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])

@router.post(
    "/",
    response_model=ProductOut,
    responses={
        200: {
            "description": "Produto criado com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "description": "Camiseta Preta",
                        "price": 49.9,
                        "barcode": "1234567890123",
                        "section": "Roupas",
                        "stock": 10,
                        "expiration_date": "2025-12-31",
                        "image": "https://exemplo.com/camiseta.jpg"
                    }
                }
            },
        },
        400: {"description": "Produto já existe."},
    },
)
def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_seller),
):
    logger = logging.getLogger(__name__)
    try:
        existing_product = db.query(Product).filter(Product.description == product_in.description).first()

        if existing_product:
            raise HTTPException(
                status_code=400,
                detail="Product with this name already exists.",
            )

        product = Product(**product_in.model_dump())  # Usando model_dump() em vez de dict()
        db.add(product)
        db.flush()  # Atualiza o ID sem fazer commit
        db.refresh(product)

        return product
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("Erro inesperado ao criar produto: %s", str(e), exc_info=True)
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Erro interno inesperado")

@router.get(
    "/",
    response_model=List[ProductOut],
    responses={
        200: {
            "description": "Lista de produtos",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "description": "Camiseta Preta",
                            "price": 49.9,
                            "barcode": "1234567890123",
                            "section": "Roupas",
                            "stock": 10,
                            "expiration_date": "2025-12-31",
                            "image": "https://exemplo.com/camiseta.jpg"
                        }
                    ]
                }
            },
        }
    },
)
def list_products(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_seller),
    description: Optional[str] = None,
    section: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
):
    """
    Lista todos os produtos cadastrados, com filtros opcionais.

    - Permite filtrar por descrição e seção.
    - Retorna os produtos paginados (parâmetros skip e limit).

    **Casos de uso:**
    - Consulta geral de produtos para venda ou estoque.
    - Busca de produtos para pedidos ou relatórios.
    """
    query = db.query(Product)

    if description:
        query = query.filter(Product.description.ilike(f"%{description}%"))
    if section:
        query = query.filter(Product.section == section)

    products = query.offset(skip).limit(limit).all()

    return products

@router.get(
    "/{product_id}",
    response_model=ProductOut,
    responses={
        200: {
            "description": "Produto encontrado",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "description": "Camiseta Preta",
                        "price": 49.9,
                        "barcode": "1234567890123",
                        "section": "Roupas",
                        "stock": 10,
                        "expiration_date": "2025-12-31",
                        "image": "https://exemplo.com/camiseta.jpg"
                    }
                }
            },
        },
        404: {"description": "Product not found."},
    },
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_seller),
):
    """
    Busca um produto pelo seu ID.

    - Retorna todos os dados do produto.
    - Retorna erro 404 caso o produto não exista.

    **Casos de uso:**
    - Visualização detalhada de um produto.
    - Consulta para edição ou análise de dados do produto.
    """
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    return product

@router.put(
    "/{product_id}",
    response_model=ProductOut,
    responses={
        200: {
            "description": "Produto atualizado",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "description": "Camiseta Preta",
                        "price": 49.9,
                        "barcode": "1234567890123",
                        "section": "Roupas",
                        "stock": 10,
                        "expiration_date": "2025-12-31",
                        "image": "https://exemplo.com/camiseta.jpg"
                    }
                }
            },
        },
        404: {"description": "Product not found."},
    },
)
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_seller),
):
    """
    Atualiza os dados de um produto existente.

    - Permite alterar descrição, preço, código de barras, seção, estoque, validade e imagem.
    - Retorna erro 404 caso o produto não exista.

    **Casos de uso:**
    - Correção de dados de produtos.
    - Atualização de informações para estoque ou vendas.
    """
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    for field, value in product_in.dict(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product

@router.delete(
    "/{product_id}",
    status_code=204,
    responses={
        204: {"description": "Produto deletado com sucesso"},
        404: {"description": "Product not found."},
    },
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_seller),
):
    """
    Remove um produto do sistema.

    - Exclui o produto permanentemente.
    - Retorna erro 404 caso o produto não exista.

    **Casos de uso:**
    - Exclusão de produtos descontinuados ou cadastrados por engano.
    - Limpeza de base de dados de produtos.
    """
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    db.delete(product)
    db.commit()

    return None
