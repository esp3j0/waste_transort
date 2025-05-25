from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator

# 从 model 中导入枚举，确保一致性
from app.models.recycling_manager import RecyclingRole

# 回收管理人员基础模型
class RecyclingManagerBase(BaseModel):
    """回收管理人员基础模型"""
    is_primary: bool = Field(False, description="是否为主要管理员")
    # role 仅在 is_primary=False 时设置，用于区分过磅员等
    role: Optional[RecyclingRole] = Field(None, description="人员角色 (例如: 过磅员)") 

    @validator('role', always=True)
    def role_required_for_non_primary(cls, v: Optional[RecyclingRole], values: Dict[str, Any]) -> Optional[RecyclingRole]:
        """如果不是主要管理员，则角色是必需的"""
        if values.get('is_primary') is False and v is None:
            raise ValueError('非主要管理员必须指定角色 (例如: 过磅员)')
        if values.get('is_primary') is True and v is not None:
            # 主要管理员不应该有具体角色如 pounder
            raise ValueError('主要管理员不应指定具体员工角色')
        return v

# 创建回收管理人员
class RecyclingManagerCreate(RecyclingManagerBase):
    """创建回收管理人员模型"""
    manager_id: int = Field(..., description="用户ID")
    recycling_company_id: int = Field(..., description="所属回收公司ID")

# 更新回收管理人员
class RecyclingManagerUpdate(BaseModel):
    """更新回收管理人员模型"""
    is_primary: Optional[bool] = Field(None, description="是否为主要管理员")
    role: Optional[RecyclingRole] = Field(None, description="人员角色")

# 回收管理人员响应模型
class RecyclingManagerResponse(RecyclingManagerBase):
    """回收管理人员响应模型"""
    id: int = Field(..., description="关联ID")
    recycling_company_id: int = Field(..., description="所属回收公司ID")
    manager_id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True 