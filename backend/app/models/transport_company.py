from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base

class TransportCompany(Base):
    """运输公司模型"""
    __tablename__ = "transport_company"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)  # 公司名称
    address = Column(String, nullable=True)  # 公司地址
    contact_name = Column(String, nullable=True)  # 联系人姓名
    contact_phone = Column(String, nullable=True)  # 联系电话
    email = Column(String, nullable=True, index=True)  # 电子邮箱
    description = Column(Text, nullable=True)  # 描述信息
    
    is_active = Column(Boolean, default=True)  # 是否激活
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间

    # 关系
    # 管理这家运输公司的人员 (TransportManager: 包含主管理员、调度员、司机)
    transport_managers = relationship("TransportManager", back_populates="transport_company", cascade="all, delete-orphan")
    # 这家运输公司拥有的车辆
    vehicles = relationship("Vehicle", back_populates="transport_company", cascade="all, delete-orphan")
    # 与这家运输公司相关的订单 (需要在 Order 模型中定义反向关系)
    orders = relationship("Order", back_populates="transport_company") 

    def __repr__(self):
        return f"<TransportCompany(id={self.id}, name='{self.name}')>" 