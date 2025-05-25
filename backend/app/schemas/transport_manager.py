from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

# 从 model 中导入枚举，确保一致性
from app.models.transport_manager import TransportRole, DriverStatus

# 运输管理人员基础模型
class TransportManagerBase(BaseModel):
    """运输管理人员基础模型"""
    is_primary: bool = Field(False, description="是否为主要管理员")
    # role 仅在 is_primary=False 时设置，用于区分调度员/司机
    role: Optional[TransportRole] = Field(None, description="人员角色 (调度员/司机)") 
    
    # 司机特有信息
    driver_license_number: Optional[str] = Field(None, description="驾驶证号 (仅司机)")
    driver_status: Optional[DriverStatus] = Field(DriverStatus.AVAILABLE, description="司机状态 (仅司机)")

    @validator('role', always=True)
    def role_required_for_non_primary(cls, v: Optional[TransportRole], values: Dict[str, Any]) -> Optional[TransportRole]:
        """如果不是主要管理员，则角色 (司机/调度员) 是必需的"""
        if values.get('is_primary') is False and v is None:
            raise ValueError('非主要管理员必须指定角色 (司机/调度员)')
        if values.get('is_primary') is True and v is not None:
            # 主要管理员不应该有 dispatcher 或 driver 的 role
            raise ValueError('主要管理员不应指定具体角色 (司机/调度员)')
        return v
    
    @validator('driver_license_number', 'driver_status', always=True)
    def driver_fields_for_drivers_only(cls, v: Optional[str], values: Dict[str, Any], field: Any) -> Optional[str]:
        """驾驶证号和司机状态仅对司机角色有效"""
        # if values.get('role') != TransportRole.DRIVER and v is not None:
        #     raise ValueError(f'{field.name} 仅适用于司机角色')
        # # 如果是司机，驾驶证号可以是必填项 (根据业务需求)
        # if values.get('role') == TransportRole.DRIVER and field.name == 'driver_license_number' and v is None:
        #     raise ValueError('司机必须提供驾驶证号')
        return v

# 创建运输管理人员
class TransportManagerCreate(TransportManagerBase):
    """创建运输管理人员模型"""
    manager_id: int = Field(..., description="用户ID")
    transport_company_id: int = Field(..., description="所属运输公司ID")

# 更新运输管理人员
class TransportManagerUpdate(BaseModel):
    """更新运输管理人员模型"""
    is_primary: Optional[bool] = Field(None, description="是否为主要管理员")
    role: Optional[TransportRole] = Field(None, description="人员角色 (调度员/司机)")
    driver_license_number: Optional[str] = Field(None, description="驾驶证号 (仅司机)")
    driver_status: Optional[DriverStatus] = Field(None, description="司机状态 (仅司机)")

    # 注意: 更新时的 validator 逻辑可能更复杂，需要考虑字段是否被实际传入
    # 例如，如果只想更新 driver_status，role 和 is_primary 不会出现在 values 中
    # 可能需要在 CRUD 层进行更复杂的校验

# 运输管理人员响应模型
class TransportManagerResponse(TransportManagerBase):
    """运输管理人员响应模型"""
    id: int = Field(..., description="关联ID")
    transport_company_id: int = Field(..., description="所属运输公司ID")
    manager_id: int = Field(..., description="用户ID")
    # 可以考虑加入 User 的基本信息，例如用户名或全名
    # manager_username: Optional[str] = None 
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True

# 单独为司机状态更新创建一个简单的 Schema
class DriverStatusUpdate(BaseModel):
    status: DriverStatus = Field(..., description="新的司机状态") 