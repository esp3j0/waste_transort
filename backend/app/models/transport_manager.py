from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base_class import Base
from app.models.user import User # 确保 User 模型可以被导入

class TransportRole(str, enum.Enum):
    """运输端人员角色枚举"""
    DISPATCHER = "dispatcher"  # 调度员
    DRIVER = "driver"        # 司机
    # 主管理员通过 is_primary 字段标识，所以这里不需要额外的角色

class DriverStatus(str, enum.Enum):
    """司机状态枚举"""
    AVAILABLE = "available"  # 可用
    BUSY = "busy"  # 忙碌
    OFF_DUTY = "off_duty"  # 休息 (例如休假或非工作时间)
    INACTIVE = "inactive"  # 未激活或已禁用

class TransportManager(Base):
    """运输管理人员模型 (关联用户、运输公司和角色)"""
    __tablename__ = "transport_manager"

    id = Column(Integer, primary_key=True, index=True)
    transport_company_id = Column(Integer, ForeignKey("transport_company.id"), nullable=False)
    manager_id = Column(Integer, ForeignKey("user.id"), nullable=False) # 关联到 User 表的 id
    
    # 角色信息
    # is_primary 为 True 代表该公司最高管理员
    is_primary = Column(Boolean, default=False, nullable=False) 
    # role 仅在 is_primary 为 False 时有意义，用于区分调度员和司机
    role = Column(SAEnum(TransportRole), nullable=True) 
    
    # 司机特有信息 (仅当 role == TransportRole.DRIVER 时相关)
    driver_license_number = Column(String, nullable=True) # 驾驶证号
    driver_status = Column(SAEnum(DriverStatus), nullable=True, default=DriverStatus.AVAILABLE) # 司机状态

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    transport_company = relationship("TransportCompany", back_populates="transport_managers")
    manager = relationship("User", back_populates="managed_transport_companies") # User.managed_transport_companies 需要在 User 模型中定义
    
    # 如果司机与特定车辆是多对一或一对一的固定关系，可以在这里添加
    # current_vehicle_id = Column(Integer, ForeignKey("vehicle.id"), nullable=True)
    # current_vehicle = relationship("Vehicle")

    # 司机负责的订单 (需要在 Order 模型中定义反向关系)
    # driver_orders = relationship("Order", back_populates="driver_manager") 

    def __repr__(self):
        return f"<TransportManager(id={self.id}, company_id={self.transport_company_id}, user_id={self.manager_id}, role={self.role}, is_primary={self.is_primary})>" 