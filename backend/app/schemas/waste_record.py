from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.user import UserResponse # For embedding user info in response

# 废物记录基础模型
class WasteRecordBase(BaseModel):
    waste_type_actual: Optional[str] = Field(None, description="实际废物类型")
    waste_volume_actual: Optional[float] = Field(None, description="实际废物体积 (立方米)")
    waste_weight_actual: Optional[float] = Field(None, description="实际废物重量 (吨)")
    processing_method: Optional[str] = Field(None, description="处理方法")
    processing_notes: Optional[str] = Field(None, description="处理备注")
    processed_at: Optional[datetime] = Field(None, description="处理完成时间")
    image_url: Optional[str] = Field(None, description="废物照片URL")
    recorded_by_user_id: Optional[int] = Field(None, description="记录人用户ID")

# 创建废物记录模型
class WasteRecordCreate(WasteRecordBase):
    order_id: int = Field(..., description="关联的订单ID")
    # recorded_by_user_id will be set based on the current user performing the action typically

# 更新废物记录模型
class WasteRecordUpdate(WasteRecordBase):
    # All fields are optional for update
    pass

# 废物记录响应模型
class WasteRecordResponse(WasteRecordBase):
    id: int = Field(..., description="废物记录ID")
    order_id: int = Field(..., description="关联的订单ID")
    recorded_at: datetime = Field(..., description="记录创建时间")
    last_updated_at: datetime = Field(..., description="记录更新时间")
    recorded_by_user: Optional[UserResponse] = Field(None, description="记录人用户信息")

    class Config:
        from_attributes = True
