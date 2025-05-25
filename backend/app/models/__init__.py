from .user import User, UserRole
# from .property import Property # 旧物业模型
from .property_company import PropertyCompany # 新物业公司模型
from .property_manager import PropertyManager
from .community import Community
from .address import Address
from .order import Order, OrderStatus
# from .transport import Transport, VehicleType, DriverStatus # 旧的 transport model

# 新的 transport 相关 models
from .transport_company import TransportCompany
from .transport_manager import TransportManager, TransportRole, DriverStatus
from .vehicle import Vehicle, VehicleType, VehicleStatus

# from .recycling import Recycling, RecyclingType, RecyclingStatus # 旧的 recycling model

# 新的 recycling 相关 models
from .recycling_company import RecyclingCompany, RecyclingCompanyType, RecyclingCompanyStatus
from .recycling_manager import RecyclingManager, RecyclingRole
from .waste_record import WasteRecord
from .payment import Payment, PaymentMethod, PaymentStatus
# from .notification import Notification, NotificationType
# from .document import Document, DocumentType
# from .feedback import Feedback
# from .statistics import Statistics # 假设有一个统计模型
# from .system_config import SystemConfig # 假设有一个系统配置模型
# from .audit_log import AuditLog # 假设有一个审计日志模型

# 导出所有模型
__all__ = [
    "User",
    "UserRole",
    "Order",
    "OrderStatus",
    "PaymentStatus",
    # "Property", # 旧
    "PropertyCompany", # 新
    "Community",
    "PropertyManager",
    "Address",
    "TransportCompany",
    "TransportManager",
    "TransportRole",
    "DriverStatus",
    "Vehicle",
    "VehicleType",
    "VehicleStatus",
    "RecyclingCompany",
    "RecyclingManager",
    "RecyclingRole",
    "WasteRecord",
    "WasteType",
    "Payment",
    "PaymentMethod",
    "PaymentStatusEnum",
    "Notification",
    "NotificationType",
    "Document",
    "DocumentType",
    "Feedback",
    "Statistics",
    "SystemConfig",
    "AuditLog",
] 