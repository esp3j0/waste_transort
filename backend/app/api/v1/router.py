from fastapi import APIRouter

from app.api.v1.endpoints import auth
from app.api.v1.endpoints import orders
from app.api.v1.endpoints import properties
from app.api.v1.endpoints import transports
from app.api.v1.endpoints import recyclings

api_router = APIRouter()

# 认证相关路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 用户相关路由将在后续实现
# api_router.include_router(users.router, prefix="/users", tags=["用户"])

# 订单相关路由
api_router.include_router(orders.router, prefix="/orders", tags=["订单"])

# 物业管理相关路由
api_router.include_router(properties.router, prefix="/properties", tags=["物业管理"])

# 运输管理相关路由
api_router.include_router(transports.router, prefix="/transports", tags=["运输管理"])

# 处置回收相关路由
api_router.include_router(recyclings.router, prefix="/recyclings", tags=["处置回收"])