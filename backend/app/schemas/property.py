from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

# 共享属性
class PropertyBase(BaseModel):
    name: str
    address: str
    contact_name: str
    contact_phone: str
    email: Optional[str] = None
    community_name: str
    building_count: Optional[int] = 0
    area: Optional[int] = 0
    household_count: Optional[int] = 0
    description: Optional[str] = None

# 创建时需要的属性
class PropertyCreate(PropertyBase):
    pass

# 更新时可以修改的属性
class PropertyUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    email: Optional[str] = None
    community_name: Optional[str] = None
    building_count: Optional[int] = None
    area: Optional[int] = None
    household_count: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    manager_id: Optional[int] = None

# API响应模型
class PropertyResponse(PropertyBase):
    id: int
    manager_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True