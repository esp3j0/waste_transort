from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class AddressBase(BaseModel):
    """地址基础模型"""
    address: str
    community_name: str
    building_number: str
    room_number: str
    contact_name: str
    contact_phone: str
    label: Optional[str] = None
    is_default: bool = False
    notes: Optional[str] = None

class AddressCreate(AddressBase):
    """创建地址模型"""
    pass

class AddressUpdate(AddressBase):
    """更新地址模型"""
    pass

class AddressResponse(AddressBase):
    """地址响应模型"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 