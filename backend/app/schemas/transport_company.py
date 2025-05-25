from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

# 导入 TransportManager 和 Vehicle 的响应模型
from .transport_manager import TransportManagerResponse 
from .vehicle import VehicleResponse

# 共享属性
class TransportCompanyBase(BaseModel):
    """运输公司基础模型"""
    name: str = Field(..., description="运输公司名称")
    address: Optional[str] = Field(None, description="公司地址")
    contact_name: Optional[str] = Field(None, description="联系人姓名")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    email: Optional[str] = Field(None, description="电子邮箱")
    description: Optional[str] = Field(None, description="描述信息")

# 创建时需要的属性
class TransportCompanyCreate(TransportCompanyBase):
    """创建运输公司模型"""
    pass

# 更新时可以修改的属性
class TransportCompanyUpdate(BaseModel):
    """更新运输公司模型"""
    name: Optional[str] = Field(None, description="运输公司名称")
    address: Optional[str] = Field(None, description="公司地址")
    contact_name: Optional[str] = Field(None, description="联系人姓名")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    email: Optional[str] = Field(None, description="电子邮箱")
    description: Optional[str] = Field(None, description="描述信息")
    is_active: Optional[bool] = Field(None, description="是否激活")

# API响应模型
class TransportCompanyResponse(TransportCompanyBase):
    """运输公司响应模型"""
    id: int = Field(..., description="运输公司ID")
    is_active: bool = Field(..., description="是否激活")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    # 关系
    transport_managers: List[TransportManagerResponse] = Field(default_factory=list, description="运输公司管理人员列表")
    vehicles: List[VehicleResponse] = Field(default_factory=list, description="运输公司车辆列表")

    class Config:
        from_attributes = True # Pydantic V2 orm_mode 替换为 from_attributes 