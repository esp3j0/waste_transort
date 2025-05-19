from fastapi import APIRouter

from app.api.v1.endpoints import properties, users

api_router = APIRouter()

# 注册各模块的路由
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(properties.router, prefix="/properties", tags=["properties"])