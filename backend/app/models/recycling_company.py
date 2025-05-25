from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base_class import Base

class RecyclingCompanyType(str, enum.Enum):
    GENERAL = "general"  # 综合回收站
    CONSTRUCTION = "construction"  # 建筑垃圾专用
    HAZARDOUS = "hazardous"  # 危险废物回收站
    ELECTRONIC = "electronic"  # 电子废物回收站
    OTHER = "other" # 其他

class RecyclingCompanyStatus(str, enum.Enum):
    ACTIVE = "active"  # 正常运营
    MAINTENANCE = "maintenance"  # 维护中
    FULL = "full"  # 容量已满 (或接近饱和，提示预警)
    INACTIVE = "inactive"  # 暂停运营或已关闭

class RecyclingCompany(Base):
    """回收公司模型"""
    __tablename__ = "recycling_company"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)  # 公司名称
    address = Column(String, nullable=True)  # 公司地址
    contact_name = Column(String, nullable=True)  # 联系人姓名
    contact_phone = Column(String, nullable=True)  # 联系电话
    email = Column(String, nullable=True, index=True)  # 电子邮箱
    description = Column(Text, nullable=True)  # 描述信息
    
    # 公司运营相关信息 (原 Recycling 模型中的字段)
    company_type = Column(SAEnum(RecyclingCompanyType), default=RecyclingCompanyType.CONSTRUCTION, nullable=False) # 回收公司类型
    status = Column(SAEnum(RecyclingCompanyStatus), default=RecyclingCompanyStatus.ACTIVE, nullable=False)  # 公司运营状态
    capacity_tons_per_day = Column(Float, nullable=True)  # 设计日处理能力（吨/天）
    current_load_tons = Column(Float, default=0.0, nullable=True)  # 当前库存或负载（吨）
    operation_hours = Column(String, nullable=True)  # 运营时间 (例如 "周一至周五 08:00-18:00")
    license_number = Column(String, nullable=True)  # 经营许可证号
    license_expiry_date = Column(DateTime, nullable=True)  # 许可证到期日期

    is_active = Column(Boolean, default=True)  # 系统中是否激活此公司记录
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    # 管理这家回收公司的人员 (RecyclingManager)
    recycling_managers = relationship("RecyclingManager", back_populates="recycling_company", cascade="all, delete-orphan")
    # 这家回收公司处理的订单
    orders = relationship("Order", back_populates="recycling_company") # Order.recycling_company 需要更新

    def __repr__(self):
        return f"<RecyclingCompany(id={self.id}, name='{self.name}')>" 