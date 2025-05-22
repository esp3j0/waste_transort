from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from enum import Enum

# 枚举类型
class VehicleType(str, Enum):
    SMALL = "small"  # 小型车辆
    MEDIUM = "medium"  # 中型车辆
    LARGE = "large"  # 大型车辆
    SPECIAL = "special"  # 特种车辆



class DriverStatus(str, Enum):
    AVAILABLE = "available"  # 可用
    BUSY = "busy"  # 忙碌
    OFF_DUTY = "off_duty"  # 休息
    INACTIVE = "inactive"  # 未激活

# 更新司机状态
class DriverStatusUpdate(BaseModel):
    status: DriverStatus

# 共享属性
class TransportBase(BaseModel):
    driver_name: str
    driver_phone: str
    driver_license: str
    vehicle_plate: str
    vehicle_type: VehicleType = VehicleType.MEDIUM
    vehicle_capacity: float
    vehicle_volume: float
    vehicle_model: Optional[str] = None
    vehicle_year: Optional[int] = None
    company_name: Optional[str] = None
    company_address: Optional[str] = None
    company_contact: Optional[str] = None
    notes: Optional[str] = None

# 创建时需要的属性
class TransportCreate(TransportBase):
    pass

# 更新时可以修改的属性
class TransportUpdate(BaseModel):
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    driver_license: Optional[str] = None
    driver_status: Optional[DriverStatus] = None
    vehicle_plate: Optional[str] = None
    vehicle_type: Optional[VehicleType] = None
    vehicle_capacity: Optional[float] = None
    vehicle_volume: Optional[float] = None
    vehicle_model: Optional[str] = None
    vehicle_year: Optional[int] = None
    company_name: Optional[str] = None
    company_address: Optional[str] = None
    company_contact: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    manager_id: Optional[int] = None

# API响应模型
class TransportResponse(TransportBase):
    id: int
    driver_status: DriverStatus
    manager_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True