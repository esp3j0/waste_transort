from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from app.schemas.community import CommunityResponse

# 共享属性
class PropertyBase(BaseModel):
    name: str
    address: str
    contact_name: str
    contact_phone: str
    email: Optional[str] = None
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
    description: Optional[str] = None
    is_active: Optional[bool] = None

# 物业管理员基础模型
class PropertyManagerBase(BaseModel):
    role: str
    is_primary: bool = False

# 创建物业管理员
class PropertyManagerCreate(PropertyManagerBase):
    manager_id: int

# 更新物业管理员
class PropertyManagerUpdate(PropertyManagerBase):
    pass

# 物业管理员响应模型
class PropertyManagerResponse(PropertyManagerBase):
    id: int
    property_id: int
    manager_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# API响应模型
class PropertyResponse(PropertyBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    property_managers: List[PropertyManagerResponse] = []
    communities: List[CommunityResponse] = []
    
    class Config:
        orm_mode = True