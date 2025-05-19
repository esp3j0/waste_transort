from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base_class import Base

class RecyclingType(str, enum.Enum):
    """回收站类型枚举"""
    GENERAL = "general"  # 综合回收站
    CONSTRUCTION = "construction"  # 建筑垃圾专用
    HAZARDOUS = "hazardous"  # 危险废物回收站
    ELECTRONIC = "electronic"  # 电子废物回收站

class RecyclingStatus(str, enum.Enum):
    """回收站状态枚举"""
    ACTIVE = "active"  # 正常运营
    MAINTENANCE = "maintenance"  # 维护中
    FULL = "full"  # 容量已满
    INACTIVE = "inactive"  # 暂停运营

class Recycling(Base):
    """回收站模型"""
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)  # 回收站名称
    address = Column(String)  # 回收站地址
    contact_name = Column(String)  # 联系人姓名
    contact_phone = Column(String)  # 联系电话
    email = Column(String, nullable=True)  # 电子邮箱
    
    # 回收站信息
    recycling_type = Column(String, default=RecyclingType.CONSTRUCTION)  # 回收站类型
    status = Column(String, default=RecyclingStatus.ACTIVE)  # 回收站状态
    capacity = Column(Float)  # 处理容量（吨/天）
    current_load = Column(Float, default=0.0)  # 当前负载（吨）
    operation_hours = Column(String, nullable=True)  # 运营时间
    
    # 许可证信息
    license_number = Column(String, nullable=True)  # 许可证号
    license_expiry = Column(DateTime, nullable=True)  # 许可证到期日
    
    # 管理信息
    manager_id = Column(Integer, ForeignKey("user.id"), nullable=True)  # 管理员ID
    manager = relationship("User", foreign_keys=[manager_id])  # 管理员
    
    # 状态信息
    is_active = Column(Boolean, default=True)  # 是否激活
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    description = Column(Text, nullable=True)  # 描述信息
    
    # 关系
    orders = relationship("Order", back_populates="recycling_station")  # 订单关系