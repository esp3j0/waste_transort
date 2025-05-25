from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.community import CommunityResponse
from app.schemas.property_manager import PropertyManagerResponse # Assuming this is already updated if needed

# 共享属性
class PropertyCompanyBase(BaseModel):
    """物业公司基础模型""" # 更新描述
    name: str = Field(..., description="物业公司名称")
    address: str = Field(..., description="物业公司地址")
    contact_name: str = Field(..., description="联系人姓名")
    contact_phone: str = Field(..., description="联系电话")
    email: Optional[str] = Field(None, description="电子邮箱")
    description: Optional[str] = Field(None, description="描述信息")

# 创建时需要的属性
class PropertyCompanyCreate(PropertyCompanyBase):
    """创建物业公司模型""" # 更新描述
    pass

# 更新时可以修改的属性
class PropertyCompanyUpdate(BaseModel):
    """更新物业公司模型""" # 更新描述
    name: Optional[str] = Field(None, description="物业公司名称")
    address: Optional[str] = Field(None, description="物业公司地址")
    contact_name: Optional[str] = Field(None, description="联系人姓名")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    email: Optional[str] = Field(None, description="电子邮箱")
    description: Optional[str] = Field(None, description="描述信息")
    is_active: Optional[bool] = Field(None, description="是否激活")

# API响应模型
class PropertyCompanyResponse(PropertyCompanyBase):
    """物业公司响应模型""" # 更新描述
    id: int = Field(..., description="物业公司ID") # 更新描述
    is_active: bool = Field(..., description="是否激活")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    property_managers: List[PropertyManagerResponse] = Field(default_factory=list, description="物业管理人员列表") # 更新描述
    communities: List[CommunityResponse] = Field(default_factory=list, description="管理的社区列表")
    
    class Config:
        from_attributes = True 