from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from enum import Enum

# 枚举类型
class RecyclingType(str, Enum):
    GENERAL = "general"  # 综合回收站
    CONSTRUCTION = "construction"  # 建筑垃圾专用
    HAZARDOUS = "hazardous"  # 危险废物回收站
    ELECTRONIC = "electronic"  # 电子废物回收站

class RecyclingStatus(str, Enum):
    ACTIVE = "active"  # 正常运营
    MAINTENANCE = "maintenance"  # 维护中
    FULL = "full"  # 容量已满
    INACTIVE = "inactive"  # 暂停运营

# 更新回收状态
class RecyclingStatusUpdate(BaseModel):
    status: RecyclingStatus

# 共享属性
class RecyclingBase(BaseModel):
    name: str
    address: str
    contact_name: str
    contact_phone: str
    email: Optional[str] = None
    recycling_type: RecyclingType = RecyclingType.CONSTRUCTION
    capacity: float
    current_load: Optional[float] = 0.0
    operation_hours: Optional[str] = None
    license_number: Optional[str] = None
    license_expiry: Optional[datetime] = None
    description: Optional[str] = None

# 创建时需要的属性
class RecyclingCreate(RecyclingBase):
    pass

# 更新时可以修改的属性
class RecyclingUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    email: Optional[str] = None
    recycling_type: Optional[RecyclingType] = None
    status: Optional[RecyclingStatus] = None
    capacity: Optional[float] = None
    current_load: Optional[float] = None
    operation_hours: Optional[str] = None
    license_number: Optional[str] = None
    license_expiry: Optional[datetime] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    manager_id: Optional[int] = None

# API响应模型
class RecyclingResponse(RecyclingBase):
    id: int
    status: RecyclingStatus
    manager_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True