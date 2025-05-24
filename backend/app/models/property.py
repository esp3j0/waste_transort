from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base

class Property(Base):
    """物业管理模型"""
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)  # 物业名称
    address = Column(String)  # 物业地址
    contact_name = Column(String)  # 联系人姓名
    contact_phone = Column(String)  # 联系电话
    email = Column(String, nullable=True)  # 电子邮箱
    
    # 状态信息
    is_active = Column(Boolean, default=True)  # 是否激活
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    description = Column(Text, nullable=True)  # 描述信息
    
    # 关系
    communities = relationship("Community", back_populates="property", cascade="all, delete-orphan")
    property_managers = relationship("PropertyManager", back_populates="property", cascade="all, delete-orphan")
    
    @property
    def primary_manager(self):
        """获取主要管理员"""
        for manager in self.property_managers:
            if manager.is_primary:
                return manager.manager
        return None