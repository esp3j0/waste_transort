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
    
    # 小区信息
    community_name = Column(String, index=True)  # 小区名称
    building_count = Column(Integer, default=0)  # 楼栋数量
    area = Column(Integer, default=0)  # 小区面积（平方米）
    household_count = Column(Integer, default=0)  # 住户数量
    
    # 物业管理员信息
    manager_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    manager = relationship("User", foreign_keys=[manager_id])
    
    # 状态信息
    is_active = Column(Boolean, default=True)  # 是否激活
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    description = Column(Text, nullable=True)  # 描述信息
    
    # 关系
    # 这里可以添加与其他模型的关系，例如与订单的关系