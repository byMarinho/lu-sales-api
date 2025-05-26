from typing import List, Optional
import logging
import sentry_sdk

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_seller, get_db
from app.integrations.whatsapp.whatsapp import send_whatsapp_message
from app.models.client import Client
from app.models.order import Order, OrderProduct, OrderStatusHistory
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderOut, OrderUpdateStatus

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "/",
    response_model=OrderOut,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Pedido criado com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "client_id": 1,
                        "status": "pending",
                        "created_at": "2025-05-25",
                        "products": [
                            {"product_id": 1, "quantity": 2},
                            {"product_id": 2, "quantity": 1}
                        ]
                    }
                }
            },
        },
        404: {"description": "Client or product not found."},
        400: {"description": "Estoque insuficiente."},
    },
)
def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_seller),
):
    logger = logging.getLogger(__name__)
    try:
        """
        Cria um novo pedido para um cliente.

        - O cliente deve existir no banco de dados.
        - Todos os produtos informados devem existir e ter estoque suficiente.
        - O estoque de cada produto é decrementado conforme a quantidade solicitada.
        - O pedido é criado com status inicial "pending".
        - Uma mensagem de WhatsApp é enviada ao cliente confirmando o recebimento do pedido.
        - Retorna o pedido criado, incluindo os produtos e quantidades.
        
        **Casos de uso:**
        - Vendedor realiza um novo pedido para um cliente já cadastrado.
        - Integração com WhatsApp para notificação automática do cliente.
        - Garante integridade de estoque e validação de existência de cliente/produto.
        """
        client = db.query(Client).filter(Client.id == order_in.client_id).first()

        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found.",
            )

        for item in order_in.products:
            product = db.query(Product).filter(Product.id == item.product_id).first()

            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with id {item.product_id} not found.",
                )

            if product.stock < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for product {product.description}.",
                )

            product.stock -= item.quantity

        order = Order(
            client_id=order_in.client_id, status="pending", created_at=order_in.created_at
        )

        db.add(order)
        db.commit()
        db.refresh(order)

        # Adiciona produtos na relação many-to-many e insere quantidade na tabela associativa
        for item in order_in.products:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                db.execute(
                    OrderProduct.insert().values(
                        order_id=order.id,
                        product_id=product.id,
                        quantity=item.quantity,
                    )
                )
        db.commit()

        send_whatsapp_message(
            client.phone,
            f"Recebemos seu pedido #{order.id}. Assim que o pagamento for aprovado te avisaremos.",
        )

        # Montar resposta no formato do schema
        result = db.execute(
            OrderProduct.select().where(OrderProduct.c.order_id == order.id)
        )
        products = [
            {"product_id": row.product_id, "quantity": row.quantity}
            for row in result.fetchall()
        ]
        order_out = OrderOut(
            id=order.id,
            client_id=order.client_id,
            status=order.status,
            created_at=order.created_at,
            products=products,
        )
        return order_out
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("Erro inesperado ao criar pedido: %s", str(e), exc_info=True)
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Erro interno inesperado")


@router.get(
    "/",
    response_model=List[OrderOut],
    responses={
        200: {
            "description": "Lista de pedidos",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "client_id": 1,
                            "status": "pending",
                            "created_at": "2025-05-25",
                            "products": [
                                {"product_id": 1, "quantity": 2}
                            ]
                        }
                    ]
                }
            },
        }
    },
)
def list_orders(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_seller),
    client_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
):
    """
    Lista todos os pedidos cadastrados, com filtros opcionais.

    - Permite filtrar por cliente, status, data de início e fim.
    - Retorna os pedidos paginados (parâmetros skip e limit).
    - Cada pedido inclui os produtos e quantidades associadas.
    
    **Casos de uso:**
    - Consulta geral de pedidos para acompanhamento.
    - Filtros para relatórios ou buscas específicas por cliente, período ou status.
    """
    query = db.query(Order)

    if client_id:
        query = query.filter(Order.client_id == client_id)
    if status:
        query = query.filter(Order.status == status)
    if start_date and end_date:
        query = query.filter(Order.created_at.between(start_date, end_date))
    if start_date and not end_date:
        query = query.filter(Order.created_at >= start_date)
    if end_date and not start_date:
        query = query.filter(Order.created_at <= end_date)

    orders = query.offset(skip).limit(limit).all()
    order_out_list = []
    for order in orders:
        result = db.execute(
            OrderProduct.select().where(OrderProduct.c.order_id == order.id)
        )
        products = [
            {"product_id": row.product_id, "quantity": row.quantity}
            for row in result.fetchall()
        ]
        order_out = OrderOut(
            id=order.id,
            client_id=order.client_id,
            status=order.status,
            created_at=order.created_at,
            products=products,
        )
        order_out_list.append(order_out)
    return order_out_list


@router.get(
    "/{order_id}",
    response_model=OrderOut,
    responses={
        200: {
            "description": "Pedido encontrado",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "client_id": 1,
                        "status": "pending",
                        "created_at": "2025-05-25",
                        "products": [
                            {"product_id": 1, "quantity": 2}
                        ]
                    }
                }
            },
        },
        404: {"description": "Order not found."},
    },
)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_seller),
):
    """
    Busca um pedido pelo seu ID.

    - Retorna todos os dados do pedido, incluindo produtos e quantidades.
    - Retorna erro 404 caso o pedido não exista.
    
    **Casos de uso:**
    - Visualização detalhada de um pedido específico.
    - Consulta para acompanhamento de status e itens do pedido.
    """
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found."
        )

    # Buscar produtos e quantidades na tabela associativa
    result = db.execute(
        OrderProduct.select().where(OrderProduct.c.order_id == order.id)
    )
    products = [
        {"product_id": row.product_id, "quantity": row.quantity}
        for row in result.fetchall()
    ]

    order_out = OrderOut(
        id=order.id,
        client_id=order.client_id,
        status=order.status,
        created_at=order.created_at,
        products=products,
    )
    return order_out


@router.put(
    "/{order_id}",
    response_model=OrderOut,
    responses={
        200: {
            "description": "Pedido atualizado com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "client_id": 1,
                        "status": "processing",
                        "created_at": "2025-05-25",
                        "products": [
                            {"product_id": 1, "quantity": 3},
                            {"product_id": 2, "quantity": 2}
                        ]
                    }
                }
            },
        },
        404: {"description": "Order not found."},
        400: {"description": "Dados inválidos ou estoque insuficiente."},
    },
)
def update_order(
    order_id: int,
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_seller),
):
    logger = logging.getLogger(__name__)
    try:
        """
        Atualiza as informações de um pedido existente (cliente, produtos e quantidades).

        - Permite alterar o cliente do pedido e os produtos/quantidades.
        - Valida existência do cliente e dos produtos, além do estoque disponível.
        - Atualiza a tabela associativa de produtos do pedido.
        - Retorna erro 404 caso o pedido não exista.
        - Retorna erro 400 caso algum produto não exista ou não haja estoque suficiente.

        **Casos de uso:**
        - Correção de pedidos lançados com informações erradas.
        - Alteração de itens ou cliente antes do processamento do pedido.
        """
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

        client = db.query(Client).filter(Client.id == order_in.client_id).first()
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found.")

        # Repor estoque dos produtos antigos
        result = db.execute(OrderProduct.select().where(OrderProduct.c.order_id == order.id))
        for row in result.fetchall():
            product = db.query(Product).filter(Product.id == row.product_id).first()
            if product:
                product.stock += row.quantity

        # Limpar produtos antigos do pedido
        db.execute(OrderProduct.delete().where(OrderProduct.c.order_id == order.id))
        db.commit()

        # Validar e atualizar produtos/quantidades
        for item in order_in.products:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with id {item.product_id} not found.")
            if product.stock < item.quantity:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Insufficient stock for product {product.description}.")
            product.stock -= item.quantity
            db.execute(OrderProduct.insert().values(order_id=order.id, product_id=product.id, quantity=item.quantity))

        order.client_id = order_in.client_id
        db.commit()
        db.refresh(order)

        # Montar resposta
        result = db.execute(OrderProduct.select().where(OrderProduct.c.order_id == order.id))
        products = [
            {"product_id": row.product_id, "quantity": row.quantity}
            for row in result.fetchall()
        ]
        order_out = OrderOut(
            id=order.id,
            client_id=order.client_id,
            status=order.status,
            created_at=order.created_at,
            products=products,
        )
        return order_out
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("Erro inesperado ao atualizar pedido: %s", str(e), exc_info=True)
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Erro interno inesperado")


@router.put(
    "/{order_id}/status",
    responses={
        200: {
            "description": "Status do pedido atualizado",
            "content": {
                "application/json": {
                    "example": {"message": "Order status updated successfully."}
                }
            },
        },
        404: {"description": "Order not found."},
    },
)
def update_order_status(
    order_id: int,
    status_update: OrderUpdateStatus,
    db: Session = Depends(get_db),
):
    """
    Atualiza o status de um pedido existente.

    - Permite alterar o status do pedido (ex: pending, processing, shipped, delivered, canceled).
    - Registra o histórico de status do pedido.
    - Envia mensagem de WhatsApp ao cliente informando a atualização do status.
    - Retorna erro 404 caso o pedido não exista.
    
    **Casos de uso:**
    - Mudança de status operacional (ex: pedido enviado, entregue, cancelado).
    - Comunicação automática com o cliente sobre o andamento do pedido.
    """
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found."
        )

    previous_status = order.status
    order.status = status_update.status

    status_hystory = OrderStatusHistory(
        order_id=order.id,
        previous_status=previous_status,
        new_status=order.status,
    )

    db.add(status_hystory)
    db.commit()

    # Buscar o cliente manualmente para garantir acesso ao telefone
    client = db.query(Client).filter(Client.id == order.client_id).first()
    if client:
        send_whatsapp_message(
            client.phone,
            f"Seu pedido # {order.id} foi atualizado para o status {order.status}.",
        )

    return {"message": "Order status updated successfully."}


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Pedido deletado com sucesso"},
        404: {"description": "Order not found."},
    },
)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_seller),
):
    """
    Remove um pedido do sistema.

    - Exclui o pedido e suas associações de produtos.
    - Retorna erro 404 caso o pedido não exista.
    
    **Casos de uso:**
    - Exclusão de pedidos criados por engano ou cancelados antes do processamento.
    - Limpeza de dados antigos ou testes.
    """
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found."
        )

    db.delete(order)
    db.commit()

    return None
