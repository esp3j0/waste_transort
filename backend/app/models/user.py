from sqlalchemy import Boolean, Column, Integer, String, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from enum import StrEnum  # Python 3.11+ 新特性

from app.db.base_class import Base

# 使用更规范的 StrEnum 定义枚举（Python 3.11+）
class UserRole(StrEnum):
    """用户角色枚举"""
    CUSTOMER = "customer"  # 用户下单端用户
    PROPERTY = "property"  # 物业管理端用户
    TRANSPORT = "transport"  # 运输管理端用户
    RECYCLING = "recycling"  # 处置回收端用户
    ADMIN = "admin"  # 系统管理员

class User(Base):
    """用户模型"""
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)  # 更推荐限定长度（如 String(50)）
    email = Column(String(255), unique=True, index=True, nullable=True)  # 邮箱建议 255 长度
    phone = Column(String(20), unique=True, index=True)  # 手机号适配国际号码长度
    hashed_password = Column(String(128), nullable=False)  # 哈希密码通常固定长度（如 SHA-256 为 64 字符）
    full_name = Column(String(50), index=True)
    
    # 关键修改：使用 SQLAlchemy 的 Enum 类型并直接绑定 UserRole 枚举类
    role = Column(
        SQLAlchemyEnum(UserRole),
        default=UserRole.CUSTOMER,  # 直接使用枚举成员，不需要 .value
        nullable=False
    )
    
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    wx_openid = Column(String(64), unique=True, index=True, nullable=True)  # 微信 OpenID 通常 64 字符

    # 关系
    addresses = relationship("Address", back_populates="user")  # 地址关系
    orders = relationship("Order", back_populates="customer", foreign_keys="Order.customer_id")
    property_orders = relationship("Order", back_populates="property_manager", foreign_keys="Order.property_manager_id")
    transport_orders = relationship("Order", back_populates="transport_manager", foreign_keys="Order.transport_manager_id")
    recycling_orders = relationship("Order", back_populates="recycling_manager", foreign_keys="Order.recycling_manager_id")
    
    # 物业管理员关系
    managed_properties = relationship("PropertyManager", back_populates="manager")
    
    # 运输管理员关系
    managed_transport_companies = relationship("TransportManager", back_populates="manager")
    
    # 回收管理员关系 (新添加)
    managed_recycling_companies = relationship("RecyclingManager", back_populates="manager")
    
    @property
    def primary_property(self):
        """获取用户作为主要管理员的物业公司"""
        for property_manager in self.managed_properties:
            if property_manager.is_primary:
                return property_manager.property
        return None