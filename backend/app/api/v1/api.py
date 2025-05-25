from fastapi import APIRouter

from app.api.v1.endpoints import (
    # properties, # 旧
    users, 
    auth, 
    orders, 
    communities,
    transport_companies,
    transport_managers,
    vehicles,
    # recycling_companies, # Will be imported with managers
    property_companies, # 新
    property_managers, # 新
    recycling_companies, # 新增，保持导入
    recycling_managers, # 新增
    waste_records, # 新增
    payments # 新增
)

api_router = APIRouter()

# 注册各模块的路由
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
# api_router.include_router(properties.router, prefix="/properties", tags=["properties"]) # 旧
api_router.include_router(property_companies.router, prefix="/property-companies", tags=["property-companies"]) # 新
api_router.include_router(property_managers.router, prefix="/property-managers", tags=["property-managers"]) # 新
api_router.include_router(communities.router, prefix="/communities", tags=["communities"])

# New Transport Endpoints
api_router.include_router(transport_companies.router, prefix="/transport-companies", tags=["transport-companies"])
api_router.include_router(transport_managers.router, prefix="/transport-managers", tags=["transport-managers"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["vehicles"])

# Updated Recycling Endpoints
api_router.include_router(recycling_companies.router, prefix="/recycling-companies", tags=["recycling-companies"])
api_router.include_router(recycling_managers.router, prefix="/recycling-managers", tags=["recycling-managers"]) # 新增

# Waste Record Endpoint
api_router.include_router(waste_records.router, prefix="/waste-records", tags=["waste-records"]) # 新增

# Payment Endpoint
api_router.include_router(payments.router, prefix="/payments", tags=["payments"]) # 新增