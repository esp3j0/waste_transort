from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

# 物业管理员基础模型
class PropertyManagerBase(BaseModel):
    """物业管理员基础模型"""
    role: str = Field(..., description="管理员角色，如：主管理员、普通管理员等")
    is_primary: bool = Field(False, description="是否为主要管理员")

# 创建物业管理员
class PropertyManagerCreate(PropertyManagerBase):
    """创建物业管理员模型"""
    manager_id: int = Field(..., description="管理员用户ID")


# 更新物业管理员
class PropertyManagerUpdate(BaseModel):
    """更新物业管理员模型"""
    role: Optional[str] = Field(None, description="管理员角色")
    is_primary: Optional[bool] = Field(None, description="是否为主要管理员")

# 物业管理员响应模型
class PropertyManagerResponse(PropertyManagerBase):
    """物业管理员响应模型"""
    id: int = Field(..., description="关联ID")
    property_id: int = Field(..., description="所属物业ID")
    manager_id: int = Field(..., description="管理员用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True 