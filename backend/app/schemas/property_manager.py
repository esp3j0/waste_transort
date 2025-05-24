from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from .community import CommunityResponse

# 物业管理员基础模型
class PropertyManagerBase(BaseModel):
    """物业管理员基础模型"""
    role: str = Field(..., description="管理员角色，如：主管理员、普通管理员等")
    is_primary: bool = Field(False, description="是否为主要管理员")
    community_id: Optional[int] = Field(None, description="关联的小区ID，非主要管理员必须提供")

    @validator('community_id', always=True)
    def community_id_required_for_non_primary(cls, v: Optional[int], values: Dict[str, Any]) -> Optional[int]:
        """如果不是主要管理员，则小区ID是必需的"""
        if values.get('is_primary') is False and v is None:
            raise ValueError('非主要管理员必须关联一个小区 (community_id is required for non-primary managers)')
        return v

# 创建物业管理员
class PropertyManagerCreate(PropertyManagerBase):
    """创建物业管理员模型"""
    manager_id: int = Field(..., description="管理员用户ID")


# 更新物业管理员
class PropertyManagerUpdate(BaseModel):
    """更新物业管理员模型"""
    role: Optional[str] = Field(None, description="管理员角色")
    is_primary: Optional[bool] = Field(None, description="是否为主要管理员")
    community_id: Optional[int] = Field(None, description="关联的小区ID")

    @validator('community_id', always=True)
    def community_id_check_on_update(cls, v: Optional[int], values: Dict[str, Any]) -> Optional[int]:
        """更新时，如果is_primary明确设置为False，则community_id必须提供"""
        # 注意: 这里的逻辑可能需要根据实际更新场景调整
        # 如果is_primary没有在本次更新中提供，我们需要获取其实际值来判断
        # 但Pydantic的validator在Update场景下，`values` 只包含本次传入的字段
        # 所以，如果is_primary=False是在数据库中但本次未更新，这个校验可能不会按预期触发
        # 更可靠的校验可能需要在CRUD操作中结合数据库当前值进行
        if values.get('is_primary') is False and v is None:
            raise ValueError('非主要管理员必须关联一个小区 (community_id is required for non-primary managers)')
        # 如果 is_primary 是 True，community_id 应该被设为 None 或者允许用户不提供/设为 None
        if values.get('is_primary') is True and v is not None:
            # 根据业务需求，也可以选择在这里自动将 community_id 设为 None，或者抛出错误
            # raise ValueError('主要管理员不能关联特定小区')
            pass # 当前允许主要管理员有关联小区ID，但通常应该为None
        return v

# 物业管理员响应模型
class PropertyManagerResponse(PropertyManagerBase):
    """物业管理员响应模型"""
    id: int = Field(..., description="关联ID")
    property_id: int = Field(..., description="所属物业ID")
    manager_id: int = Field(..., description="管理员用户ID")
    community: Optional[CommunityResponse] = Field(None, description="关联的小区信息")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True 