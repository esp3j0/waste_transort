from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base

class PropertyCompany(Base):
    __tablename__ = "property_company" # 新增表名
    """物业公司模型""" # 更新描述
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)  # 物业公司名称
    address = Column(String)  # 物业公司地址
    contact_name = Column(String)  # 联系人姓名
    contact_phone = Column(String)  # 联系电话
    email = Column(String, nullable=True)  # 电子邮箱
    
    # 状态信息
    is_active = Column(Boolean, default=True)  # 是否激活
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    description = Column(Text, nullable=True)  # 描述信息
    
    # 关系
    # "Community.property_company" and "PropertyManager.property_company"
    communities = relationship("Community", back_populates="property_company", cascade="all, delete-orphan")
    property_managers = relationship("PropertyManager", back_populates="property_company", cascade="all, delete-orphan")
    
    # renovations = relationship("Renovation", back_populates="property_company") # 新增，如果Renovation需要反向关联

    @property
    def primary_manager_user(self): # Renamed for clarity
        """获取主要管理员的用户对象"""
        for manager_assoc in self.property_managers:
            if manager_assoc.is_primary:
                return manager_assoc.manager # manager is the User object from PropertyManager
        return None

    def __repr__(self):
        return f"<PropertyCompany(id={self.id}, name='{self.name}')>" 