from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base_class import Base

class OrderStatus(str, enum.Enum):
    """订单状态枚举"""
    PENDING = "pending"  # 待处理
    PROPERTY_CONFIRMED = "property_confirmed"  # 物业确认
    TRANSPORT_ASSIGNED = "transport_assigned"  # 已分配运输
    TRANSPORTING = "transporting"  # 运输中
    DELIVERED = "delivered"  # 已送达回收站
    RECYCLING_CONFIRMED = "recycling_confirmed"  # 回收站确认
    COMPLETED = "completed"  # 完成
    CANCELLED = "cancelled"  # 取消

class RenovationStatus(str, enum.Enum):
    """装修报备状态枚举"""
    PENDING = "pending"  # 待审核
    APPROVED = "approved"  # 已批准
    REJECTED = "rejected"  # 已拒绝
    IN_PROGRESS = "in_progress"  # 装修中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消

class RenovationType(str, enum.Enum):
    """装修类型枚举"""
    FULL = "full"  # 全屋装修
    PARTIAL = "partial"  # 局部装修
    MINOR = "minor"  # 小规模装修
    MAINTENANCE = "maintenance"  # 维修

class Order(Base):
    """订单模型"""
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True)  # 订单编号
    
    # 客户信息
    customer_id = Column(Integer, ForeignKey("user.id"))
    customer = relationship("User", back_populates="orders", foreign_keys=[customer_id])
    address_id = Column(Integer, ForeignKey("address.id"))  # 地址ID
    address = relationship("Address")  # 地址关系
    
    # 订单信息
    waste_type = Column(String)  # 垃圾类型
    waste_volume = Column(Float)  # 垃圾体积（立方米）
    waste_weight = Column(Float, nullable=True)  # 垃圾重量（吨）
    expected_pickup_time = Column(DateTime, nullable=True)  # 预期取件时间
    actual_pickup_time = Column(DateTime, nullable=True)  # 实际取件时间
    delivery_time = Column(DateTime, nullable=True)  # 送达回收站时间
    notes = Column(Text, nullable=True)  # 备注
    
    # 物业管理信息
    property_manager_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    property_manager = relationship("User", back_populates="property_orders", foreign_keys=[property_manager_id])
    property_confirm_time = Column(DateTime, nullable=True)  # 物业确认时间
    property_notes = Column(Text, nullable=True)  # 物业备注
    
    # 运输管理信息
    transport_manager_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    transport_manager = relationship("User", back_populates="transport_orders", foreign_keys=[transport_manager_id])
    driver_id = Column(Integer, ForeignKey("transport.id"), nullable=True)  # 司机ID
    driver = relationship("Transport", back_populates="orders")  # 司机信息
    vehicle_plate = Column(String, nullable=True)  # 车牌号
    transport_route = Column(String, nullable=True)  # 运输路线
    transport_notes = Column(Text, nullable=True)  # 运输备注
    
    # 处置回收信息
    recycling_manager_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    recycling_manager = relationship("User", back_populates="recycling_orders", foreign_keys=[recycling_manager_id])
    recycling_station_id = Column(Integer, ForeignKey("recycling.id"), nullable=True)  # 回收站ID
    recycling_station = relationship("Recycling", back_populates="orders")  # 回收站信息
    recycling_confirm_time = Column(DateTime, nullable=True)  # 回收确认时间
    recycling_notes = Column(Text, nullable=True)  # 回收备注
    
    # 订单状态和时间
    status = Column(String, default=OrderStatus.PENDING)  # 订单状态
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    # 费用信息
    price = Column(Float, default=0.0)  # 订单价格
    payment_status = Column(String, default="unpaid")  # 支付状态
    payment_time = Column(DateTime, nullable=True)  # 支付时间

class Renovation(Base):
    """装修报备模型"""
    id = Column(Integer, primary_key=True, index=True)
    renovation_number = Column(String, unique=True, index=True)  # 报备编号
    
    # 基本信息
    customer_id = Column(Integer, ForeignKey("user.id"))  # 报备人ID
    customer = relationship("User", foreign_keys=[customer_id])  # 报备人信息
    address_id = Column(Integer, ForeignKey("address.id"))  # 地址ID
    address = relationship("Address")  # 地址关系
    
    # 装修信息
    renovation_type = Column(String, default=RenovationType.PARTIAL)  # 装修类型
    start_date = Column(DateTime)  # 计划开始时间
    end_date = Column(DateTime)  # 计划结束时间
    actual_start_date = Column(DateTime, nullable=True)  # 实际开始时间
    actual_end_date = Column(DateTime, nullable=True)  # 实际结束时间
    
    # 装修公司信息
    company_name = Column(String, nullable=True)  # 装修公司名称
    company_contact = Column(String, nullable=True)  # 装修公司联系人
    company_phone = Column(String, nullable=True)  # 装修公司电话
    
    # 装修内容
    description = Column(Text)  # 装修内容描述
    scope = Column(Text)  # 装修范围
    materials = Column(Text, nullable=True)  # 主要材料清单
    
    # 物业信息
    property_id = Column(Integer, ForeignKey("property.id"))  # 物业ID
    property = relationship("Property", foreign_keys=[property_id])  # 物业信息
    property_manager_id = Column(Integer, ForeignKey("user.id"), nullable=True)  # 物业审核人ID
    property_manager = relationship("User", foreign_keys=[property_manager_id])  # 物业审核人
    
    # 审核信息
    status = Column(String, default=RenovationStatus.PENDING)  # 报备状态
    review_time = Column(DateTime, nullable=True)  # 审核时间
    review_notes = Column(Text, nullable=True)  # 审核意见
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    # 其他信息
    notes = Column(Text, nullable=True)  # 备注
    attachments = Column(Text, nullable=True)  # 附件（可以存储文件路径或URL）