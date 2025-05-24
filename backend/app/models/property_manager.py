from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base

class PropertyManager(Base):
    """物业管理员关联表"""
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("property.id"), nullable=False)
    manager_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    role = Column(String, nullable=False)  # 管理员角色，如：主管理员、普通管理员等
    is_primary = Column(Boolean, default=False)  # 是否为主要管理员
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    property = relationship("Property", back_populates="property_managers")
    manager = relationship("User", back_populates="managed_properties") 