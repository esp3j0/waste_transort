from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base_class import Base

class VehicleType(str, enum.Enum):
    """车辆类型枚举"""
    SMALL = "small"  # 小型车辆
    MEDIUM = "medium"  # 中型车辆
    LARGE = "large"  # 大型车辆
    SPECIAL = "special"  # 特种车辆

class DriverStatus(str, enum.Enum):
    """司机状态枚举"""
    AVAILABLE = "available"  # 可用
    BUSY = "busy"  # 忙碌
    OFF_DUTY = "off_duty"  # 休息
    INACTIVE = "inactive"  # 未激活

class Transport(Base):
    """运输管理模型"""
    id = Column(Integer, primary_key=True, index=True)
    driver_name = Column(String, index=True)  # 司机姓名
    driver_phone = Column(String)  # 司机电话
    driver_license = Column(String)  # 驾驶证号
    driver_status = Column(String, default=DriverStatus.AVAILABLE)  # 司机状态
    
    # 车辆信息
    vehicle_plate = Column(String, index=True)  # 车牌号
    vehicle_type = Column(String, default=VehicleType.MEDIUM)  # 车辆类型
    vehicle_capacity = Column(Float)  # 车辆载重量（吨）
    vehicle_volume = Column(Float)  # 车辆容积（立方米）
    vehicle_model = Column(String, nullable=True)  # 车辆型号
    vehicle_year = Column(Integer, nullable=True)  # 车辆年份
    
    # 运输公司信息
    company_name = Column(String, nullable=True)  # 公司名称
    company_address = Column(String, nullable=True)  # 公司地址
    company_contact = Column(String, nullable=True)  # 公司联系人
    
    # 管理信息
    manager_id = Column(Integer, ForeignKey("user.id"), nullable=True)  # 管理员ID
    manager = relationship("User", foreign_keys=[manager_id])  # 管理员
    
    # 状态信息
    is_active = Column(Boolean, default=True)  # 是否激活
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    notes = Column(Text, nullable=True)  # 备注
    
    # 关系
    orders = relationship("Order", back_populates="driver")  # 订单关系