from sqlalchemy import Boolean, Column, Integer, String, Enum
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class UserRole(str, Enum):
    """用户角色枚举"""
    CUSTOMER = "customer"  # 用户下单端用户
    PROPERTY = "property"  # 物业管理端用户
    TRANSPORT = "transport"  # 运输管理端用户
    RECYCLING = "recycling"  # 处置回收端用户
    ADMIN = "admin"  # 系统管理员

class User(Base):
    """用户模型"""
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, index=True)
    role = Column(String, default=UserRole.CUSTOMER)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    wx_openid = Column(String, unique=True, index=True, nullable=True)
    
    # 关系
    orders = relationship("Order", back_populates="customer", foreign_keys="Order.customer_id")
    property_orders = relationship("Order", back_populates="property_manager", foreign_keys="Order.property_manager_id")
    transport_orders = relationship("Order", back_populates="transport_manager", foreign_keys="Order.transport_manager_id")
    recycling_orders = relationship("Order", back_populates="recycling_manager", foreign_keys="Order.recycling_manager_id")