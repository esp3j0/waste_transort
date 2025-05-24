from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base
from app.models.community import Community # 导入 Community 模型

class Address(Base):
    """地址模型"""
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))  # 用户ID
    user = relationship("User", back_populates="addresses")  # 用户关系
    
    # 地址信息
    address = Column(String)  # 详细地址 (例如：xx路xx号)
    community_id = Column(Integer, ForeignKey("community.id"), nullable=False) # 新增：关联小区ID
    building_number = Column(String)  # 楼栋号
    room_number = Column(String)  # 房间号
    contact_name = Column(String)  # 联系人姓名
    contact_phone = Column(String)  # 联系电话
    
    # 关联的小区对象
    community = relationship("Community") # 新增：与Community模型的关系
    
    # 地址标签
    label = Column(String, nullable=True)  # 地址标签（如：家、公司等）
    is_default = Column(Boolean, default=False)  # 是否默认地址
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    # 其他信息
    notes = Column(Text, nullable=True)  # 备注 