from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base

class PropertyManager(Base):
    """物业管理员关联表"""
    id = Column(Integer, primary_key=True, index=True)
    # property_id = Column(Integer, ForeignKey("property.id"), nullable=False) # 旧外键
    property_company_id = Column(Integer, ForeignKey("property_company.id"), nullable=False) # 新外键
    manager_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    role = Column(String, nullable=False)  # 管理员角色，如：主管理员、普通管理员等
    is_primary = Column(Boolean, default=False)  # 是否为主要管理员
    community_id = Column(Integer, ForeignKey("community.id"), nullable=True) # 关联的小区ID，对于非主要管理员
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    # property = relationship("Property", back_populates="property_managers") # 旧关系
    property_company = relationship("PropertyCompany", back_populates="property_managers") # 新关系
    manager = relationship("User", back_populates="managed_properties")
    community = relationship("Community") # 关联的小区对象

    def __repr__(self):
        return f"<PropertyManager(id={self.id}, property_company_id={self.property_company_id}, manager_id={self.manager_id}, role={self.role}, is_primary={self.is_primary})>" # 更新 repr 