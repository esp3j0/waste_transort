from .user import UserBase, UserCreate, UserUpdate, UserResponse, UserRole, Token, TokenPayload
# from .property import PropertyBase, PropertyCreate, PropertyUpdate, PropertyResponse # 旧
from .property_company import PropertyCompanyBase, PropertyCompanyCreate, PropertyCompanyUpdate, PropertyCompanyResponse # 新
from .property_manager import PropertyManagerBase, PropertyManagerCreate, PropertyManagerUpdate, PropertyManagerResponse # 新
from .community import CommunityBase, CommunityCreate, CommunityUpdate, CommunityResponse
from .address import AddressBase, AddressCreate, AddressUpdate, AddressResponse
from .order import OrderBase, OrderCreate, OrderUpdate, OrderStatusUpdate, OrderResponse, OrderStatus
# from .renovation import RenovationBase, RenovationCreate, RenovationUpdate, RenovationResponse # 装修备案暂未实现
# from .transport import TransportBase, TransportCreate, TransportUpdate, TransportResponse, TransportStatus, TransportType # 旧
from .transport_company import TransportCompanyBase, TransportCompanyCreate, TransportCompanyUpdate, TransportCompanyResponse
from .transport_manager import TransportManagerBase, TransportManagerCreate, TransportManagerUpdate, TransportManagerResponse, DriverStatusUpdate, TransportRole, DriverStatus
from .vehicle import VehicleBase, VehicleCreate, VehicleUpdate, VehicleResponse, VehicleStatus
# from .recycling import RecyclingBase, RecyclingCreate, RecyclingUpdate, RecyclingResponse, RecyclingType, RecyclingStatus # 旧
from .recycling_company import RecyclingCompanyBase, RecyclingCompanyCreate, RecyclingCompanyUpdate, RecyclingCompanyStatusUpdate, RecyclingCompanyResponse, RecyclingCompanyType, RecyclingCompanyStatus
from .recycling_manager import RecyclingManagerBase, RecyclingManagerCreate, RecyclingManagerUpdate, RecyclingManagerResponse, RecyclingRole
from .waste_record import WasteRecordBase, WasteRecordCreate, WasteRecordUpdate, WasteRecordResponse
from .payment import PaymentBase, PaymentCreate, PaymentUpdate, PaymentResponse, PaymentMethod, PaymentStatus # 新增

__all__ = [
    "UserBase", "UserCreate", "UserUpdate", "UserResponse", "UserRole", "Token", "TokenPayload",
    "PropertyCompanyBase", "PropertyCompanyCreate", "PropertyCompanyUpdate", "PropertyCompanyResponse",
    "PropertyManagerBase", "PropertyManagerCreate", "PropertyManagerUpdate", "PropertyManagerResponse",
    "CommunityBase", "CommunityCreate", "CommunityUpdate", "CommunityResponse",
    "AddressBase", "AddressCreate", "AddressUpdate", "AddressResponse",
    "OrderBase", "OrderCreate", "OrderUpdate", "OrderStatusUpdate", "OrderResponse", "OrderStatus",
    "RenovationBase", "RenovationCreate", "RenovationUpdate", "RenovationResponse",
    "TransportCompanyBase", "TransportCompanyCreate", "TransportCompanyUpdate", "TransportCompanyResponse",
    "TransportManagerBase", "TransportManagerCreate", "TransportManagerUpdate", "TransportManagerResponse", "DriverStatusUpdate", "TransportRole", "DriverStatus",
    "VehicleBase", "VehicleCreate", "VehicleUpdate", "VehicleResponse", "VehicleStatus",
    "RecyclingCompanyBase", "RecyclingCompanyCreate", "RecyclingCompanyUpdate", "RecyclingCompanyStatusUpdate", "RecyclingCompanyResponse", "RecyclingCompanyType", "RecyclingCompanyStatus",
    "RecyclingManagerBase", "RecyclingManagerCreate", "RecyclingManagerUpdate", "RecyclingManagerResponse", "RecyclingRole",
    "WasteRecordBase", "WasteRecordCreate", "WasteRecordUpdate", "WasteRecordResponse",
    "PaymentBase", "PaymentCreate", "PaymentUpdate", "PaymentResponse", "PaymentMethod", "PaymentStatus" # 新增
]