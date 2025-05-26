from fastapi import APIRouter

from app.api.v1.endpoints import auth, client, order, product

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(client.router)
api_router.include_router(product.router)
api_router.include_router(order.router)
