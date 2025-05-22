from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

# 基础模型
class CommunityBase(BaseModel):
    """社区基础模型"""
    name: str = Field(..., description="社区名称")
    address: str = Field(..., description="社区地址")
    description: Optional[str] = Field(None, description="社区描述")
    is_active: bool = Field(True, description="是否激活")

# 创建模型
class CommunityCreate(CommunityBase):
    """创建社区模型"""
    pass

# 更新模型
class CommunityUpdate(BaseModel):
    """更新社区模型"""
    name: Optional[str] = Field(None, description="社区名称")
    address: Optional[str] = Field(None, description="社区地址")
    description: Optional[str] = Field(None, description="社区描述")
    is_active: Optional[bool] = Field(None, description="是否激活")

# 响应模型
class CommunityResponse(CommunityBase):
    """社区响应模型"""
    id: int = Field(..., description="社区ID")
    property_id: int = Field(..., description="所属物业ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True 