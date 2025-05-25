from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

# 从 model 中导入枚举，确保一致性
from app.models.vehicle import VehicleType, VehicleStatus

# 车辆基础模型
class VehicleBase(BaseModel):
    """车辆基础模型"""
    plate_number: str = Field(..., description="车牌号")
    vehicle_type: VehicleType = Field(VehicleType.MEDIUM, description="车辆类型")
    model_name: Optional[str] = Field(None, description="车辆型号")
    purchase_year: Optional[int] = Field(None, description="购置年份")
    capacity_tons: Optional[float] = Field(None, description="额定载重量 (吨)")
    volume_cubic_meters: Optional[float] = Field(None, description="额定容积 (立方米)")
    status: VehicleStatus = Field(VehicleStatus.AVAILABLE, description="车辆当前状态")
    notes: Optional[str] = Field(None, description="备注信息")

# 创建车辆模型
class VehicleCreate(VehicleBase):
    """创建车辆模型"""
    transport_company_id: int = Field(..., description="所属运输公司ID")

# 更新车辆模型
class VehicleUpdate(BaseModel):
    """更新车辆模型"""
    plate_number: Optional[str] = Field(None, description="车牌号")
    vehicle_type: Optional[VehicleType] = Field(None, description="车辆类型")
    model_name: Optional[str] = Field(None, description="车辆型号")
    purchase_year: Optional[int] = Field(None, description="购置年份")
    capacity_tons: Optional[float] = Field(None, description="额定载重量 (吨)")
    volume_cubic_meters: Optional[float] = Field(None, description="额定容积 (立方米)")
    status: Optional[VehicleStatus] = Field(None, description="车辆当前状态")
    notes: Optional[str] = Field(None, description="备注信息")
    is_active: Optional[bool] = Field(None, description="是否激活")
    # transport_company_id: Optional[int] = Field(None, description="所属运输公司ID (一般不建议修改)")

# 车辆状态更新模型
class VehicleStatusUpdate(BaseModel):
    """车辆状态更新模型"""
    status: VehicleStatus = Field(..., description="车辆目标状态")

    @validator('status')
    def validate_status_enum(cls, v):
        if not isinstance(v, VehicleStatus):
            try:
                return VehicleStatus(v) #尝试从字符串转换
            except ValueError:
                raise ValueError(f'无效的车辆状态: {v}. 必须是 {VehicleStatus.__members__.keys()} 之一')
        return v

# 车辆响应模型
class VehicleResponse(VehicleBase):
    """车辆响应模型"""
    id: int = Field(..., description="车辆ID")
    transport_company_id: int = Field(..., description="所属运输公司ID")
    is_active: bool = Field(..., description="是否激活")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True 