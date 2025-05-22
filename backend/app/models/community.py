from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base

class Community(Base):
    """小区信息模型"""
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)  # 小区名称
    address = Column(String)  # 小区地址
    building_count = Column(Integer, default=0)  # 楼栋数量
    area = Column(Integer, default=0)  # 小区面积（平方米）
    household_count = Column(Integer, default=0)  # 住户数量
    description = Column(Text, nullable=True)  # 描述信息
    is_active = Column(Boolean, default=True)  # 是否激活
    
    # 关联物业公司
    property_id = Column(Integer, ForeignKey("property.id"), nullable=False)
    property = relationship("Property", back_populates="communities")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间 