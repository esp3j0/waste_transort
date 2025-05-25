from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

# 从 model 导入枚举
from app.models.recycling_company import RecyclingCompanyType, RecyclingCompanyStatus

# 导入 RecyclingManager 的响应模型
from .recycling_manager import RecyclingManagerResponse 

# 共享属性
class RecyclingCompanyBase(BaseModel):
    """回收公司基础模型"""
    name: str = Field(..., description="回收公司名称")
    address: Optional[str] = Field(None, description="公司地址")
    contact_name: Optional[str] = Field(None, description="联系人姓名")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    email: Optional[str] = Field(None, description="电子邮箱")
    description: Optional[str] = Field(None, description="描述信息")
    
    company_type: RecyclingCompanyType = Field(RecyclingCompanyType.CONSTRUCTION, description="回收公司类型")
    status: RecyclingCompanyStatus = Field(RecyclingCompanyStatus.ACTIVE, description="公司运营状态")
    capacity_tons_per_day: Optional[float] = Field(None, description="设计日处理能力（吨/天）")
    current_load_tons: Optional[float] = Field(0.0, description="当前库存或负载（吨）")
    operation_hours: Optional[str] = Field(None, description="运营时间")
    license_number: Optional[str] = Field(None, description="经营许可证号")
    license_expiry_date: Optional[datetime] = Field(None, description="许可证到期日期")

# 创建时需要的属性
class RecyclingCompanyCreate(RecyclingCompanyBase):
    """创建回收公司模型"""
    pass

# 更新时可以修改的属性
class RecyclingCompanyUpdate(BaseModel):
    """更新回收公司模型"""
    name: Optional[str] = Field(None, description="回收公司名称")
    address: Optional[str] = Field(None, description="公司地址")
    contact_name: Optional[str] = Field(None, description="联系人姓名")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    email: Optional[str] = Field(None, description="电子邮箱")
    description: Optional[str] = Field(None, description="描述信息")
    
    company_type: Optional[RecyclingCompanyType] = Field(None, description="回收公司类型")
    status: Optional[RecyclingCompanyStatus] = Field(None, description="公司运营状态")
    capacity_tons_per_day: Optional[float] = Field(None, description="设计日处理能力（吨/天）")
    current_load_tons: Optional[float] = Field(None, description="当前库存或负载（吨）")
    operation_hours: Optional[str] = Field(None, description="运营时间")
    license_number: Optional[str] = Field(None, description="经营许可证号")
    license_expiry_date: Optional[datetime] = Field(None, description="许可证到期日期")
    is_active: Optional[bool] = Field(None, description="是否激活")

# 单独为回收站状态更新创建一个简单的 Schema
class RecyclingCompanyStatusUpdate(BaseModel):
    status: RecyclingCompanyStatus = Field(..., description="新的回收公司运营状态")
    current_load_tons: Optional[float] = Field(None, description="更新当前负载 (可选)")

# API响应模型
class RecyclingCompanyResponse(RecyclingCompanyBase):
    """回收公司响应模型"""
    id: int = Field(..., description="回收公司ID")
    is_active: bool = Field(..., description="是否激活")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    # 关系
    recycling_managers: List[RecyclingManagerResponse] = Field(default_factory=list, description="回收公司管理人员列表")

    class Config:
        from_attributes = True 