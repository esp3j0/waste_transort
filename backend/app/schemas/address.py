from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from .community import CommunityResponse

class AddressBase(BaseModel):
    """地址基础模型"""
    address: str = Field(..., description="详细街道地址，例如xx路xx号")
    community_id: int = Field(..., description="关联的小区ID")
    building_number: str = Field(..., description="楼栋号")
    room_number: str = Field(..., description="房间号")
    contact_name: str = Field(..., description="联系人姓名")
    contact_phone: str = Field(..., description="联系电话")
    label: Optional[str] = Field(None, description="地址标签，如家、公司")
    is_default: bool = Field(False, description="是否为默认地址")
    notes: Optional[str] = Field(None, description="备注")

class AddressCreate(AddressBase):
    """创建地址模型"""
    pass

class AddressUpdate(BaseModel):
    """更新地址模型"""
    address: Optional[str] = Field(None, description="详细街道地址")
    community_id: Optional[int] = Field(None, description="关联的小区ID")
    building_number: Optional[str] = Field(None, description="楼栋号")
    room_number: Optional[str] = Field(None, description="房间号")
    contact_name: Optional[str] = Field(None, description="联系人姓名")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    label: Optional[str] = Field(None, description="地址标签")
    is_default: Optional[bool] = Field(None, description="是否为默认地址")
    notes: Optional[str] = Field(None, description="备注")

class AddressResponse(AddressBase):
    """地址响应模型"""
    id: int
    user_id: int
    community: Optional[CommunityResponse] = Field(None, description="关联的小区详细信息")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 