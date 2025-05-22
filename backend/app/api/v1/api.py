from fastapi import APIRouter

from app.api.v1.endpoints import properties, users, auth, orders, transports, recyclings

api_router = APIRouter()

# 注册各模块的路由
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(properties.router, prefix="/properties", tags=["properties"])
api_router.include_router(transports.router, prefix="/transports", tags=["transports"])
api_router.include_router(recyclings.router, prefix="/recyclings", tags=["recyclings"])