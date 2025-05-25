from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base
from app.models.user import User # For recorded_by_user relationship

class WasteRecord(Base):
    """废物记录模型，记录订单相关的实际废物信息"""
    __tablename__ = "waste_record"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("order.id"), nullable=False, index=True)
    
    # 实际废物信息，可能在运输或回收环节记录/更新
    waste_type_actual = Column(String, nullable=True, comment="实际废物类型")
    waste_volume_actual = Column(Float, nullable=True, comment="实际废物体积 (立方米)")
    waste_weight_actual = Column(Float, nullable=True, comment="实际废物重量 (吨)")
    
    # 处理信息
    processing_method = Column(String, nullable=True, comment="处理方法，如：填埋、回收、焚烧")
    processing_notes = Column(Text, nullable=True, comment="处理备注")
    processed_at = Column(DateTime, nullable=True, comment="处理完成时间")

    # 其他信息
    image_url = Column(String, nullable=True, comment="废物照片URL")
    recorded_at = Column(DateTime, default=datetime.utcnow, comment="记录创建时间")
    last_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="记录更新时间")
    
    recorded_by_user_id = Column(Integer, ForeignKey("user.id"), nullable=True, comment="记录人用户ID")
    
    # 关系
    order = relationship("Order", back_populates="waste_records")
    recorded_by_user = relationship("User") # Simple relationship, no back_populates needed on User for this

    def __repr__(self):
        return f"<WasteRecord(id={self.id}, order_id={self.order_id}, type='{self.waste_type_actual}')>"
