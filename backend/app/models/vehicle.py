from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base_class import Base

class VehicleType(str, enum.Enum):
    """车辆类型枚举"""
    SMALL = "small"      # 小型货车 (例如: 微型面包车、小型厢式货车)
    MEDIUM = "medium"    # 中型货车 (例如: 4.2米厢式货车、平板车)
    LARGE = "large"      # 大型货车 (例如: 6.8米、9.6米高栏车、厢式车)
    SPECIAL = "special"  # 特种车辆 (例如: 压缩式垃圾车、自卸车)
    OTHER = "other"      # 其他类型

class VehicleStatus(str, enum.Enum):
    """车辆状态枚举"""
    AVAILABLE = "available"  # 可用
    IN_USE = "in_use"        # 使用中/运输中
    MAINTENANCE = "maintenance" # 维修中
    INACTIVE = "inactive"    # 未激活/已停用

class Vehicle(Base):
    """车辆信息模型"""
    __tablename__ = "vehicle"

    id = Column(Integer, primary_key=True, index=True)
    transport_company_id = Column(Integer, ForeignKey("transport_company.id"), nullable=False) # 所属运输公司
    
    plate_number = Column(String, index=True, unique=True, nullable=False)  # 车牌号
    vehicle_type = Column(SAEnum(VehicleType), nullable=False, default=VehicleType.MEDIUM)  # 车辆类型
    model_name = Column(String, nullable=True)  # 车辆型号 (例如: 解放J6, 东风天龙)
    purchase_year = Column(Integer, nullable=True)  # 购置年份
    
    # 载重和容积
    capacity_tons = Column(Float, nullable=True)  # 额定载重量（吨）
    volume_cubic_meters = Column(Float, nullable=True)  # 额定容积（立方米）
    
    # 状态与管理
    status = Column(SAEnum(VehicleStatus), nullable=False, default=VehicleStatus.AVAILABLE)  # 车辆当前状态
    is_active = Column(Boolean, default=True) # 是否在系统中激活可用 (区别于临时状态)
    notes = Column(String, nullable=True) # 备注信息 (例如: 保险到期日, 年检信息)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    transport_company = relationship("TransportCompany", back_populates="vehicles")
    
    # 与司机的关系：一辆车可以被多个司机驾驶 (如果需要记录历史驾驶员或当前驾驶员)
    # 或者一个司机可以驾驶多辆车。如果需要更复杂的关系，可能需要一个关联表。
    # 如果一个司机在某个时间段固定驾驶某辆车，可以在 TransportManager 中关联 Vehicle。
    # current_driver_id = Column(Integer, ForeignKey("transport_manager.id"), nullable=True)
    # current_driver = relationship("TransportManager", back_populates="driven_vehicle") # TransportManager 中需要 driven_vehicle 关系

    # 与订单的关系 (一辆车可以执行多个订单)
    # orders = relationship("Order", back_populates="vehicle") # Order 模型中需要 vehicle 关系

    def __repr__(self):
        return f"<Vehicle(id={self.id}, plate_number='{self.plate_number}', company_id={self.transport_company_id})>" 