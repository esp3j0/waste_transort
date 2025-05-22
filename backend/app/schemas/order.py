from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from enum import Enum
from .address import AddressResponse

# 订单状态枚举
class OrderStatus(str, Enum):
    PENDING = "pending"  # 待处理
    PROPERTY_CONFIRMED = "property_confirmed"  # 物业确认
    TRANSPORT_ASSIGNED = "transport_assigned"  # 已分配运输
    TRANSPORTING = "transporting"  # 运输中
    DELIVERED = "delivered"  # 已送达回收站
    RECYCLING_CONFIRMED = "recycling_confirmed"  # 回收站确认
    COMPLETED = "completed"  # 完成
    CANCELLED = "cancelled"  # 取消

# 共享属性
class OrderBase(BaseModel):
    # 地址信息
    address_id: int
    
    # 订单信息
    waste_type: str
    waste_volume: float
    expected_pickup_time: Optional[datetime] = None
    notes: Optional[str] = None

# 创建时需要的属性
class OrderCreate(OrderBase):
    pass

# 更新订单状态
class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    property_notes: Optional[str] = None
    transport_notes: Optional[str] = None
    recycling_notes: Optional[str] = None
    driver_id: Optional[int] = None
    vehicle_plate: Optional[str] = None
    transport_route: Optional[str] = None
    recycling_station_id: Optional[int] = None
    waste_weight: Optional[float] = None
    actual_pickup_time: Optional[datetime] = None
    delivery_time: Optional[datetime] = None
    recycling_confirm_time: Optional[datetime] = None

# 更新时可以修改的属性
class OrderUpdate(BaseModel):
    # 客户信息
    customer_address: Optional[str] = None
    community_name: Optional[str] = None
    building_number: Optional[str] = None
    room_number: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    
    # 订单信息
    waste_type: Optional[str] = None
    waste_volume: Optional[float] = None
    waste_weight: Optional[float] = None
    expected_pickup_time: Optional[datetime] = None
    actual_pickup_time: Optional[datetime] = None
    delivery_time: Optional[datetime] = None
    notes: Optional[str] = None
    
    # 物业管理信息
    property_manager_id: Optional[int] = None
    property_confirm_time: Optional[datetime] = None
    property_notes: Optional[str] = None
    
    # 运输管理信息
    transport_manager_id: Optional[int] = None
    driver_id: Optional[int] = None
    vehicle_plate: Optional[str] = None
    transport_route: Optional[str] = None
    transport_notes: Optional[str] = None
    
    # 处置回收信息
    recycling_manager_id: Optional[int] = None
    recycling_station_id: Optional[int] = None
    recycling_confirm_time: Optional[datetime] = None
    recycling_notes: Optional[str] = None
    
    # 订单状态
    status: Optional[OrderStatus] = None
    
    # 费用信息
    price: Optional[float] = None
    payment_status: Optional[str] = None
    payment_time: Optional[datetime] = None

# API响应模型
class OrderResponse(OrderBase):
    id: int
    order_number: str
    customer_id: int
    
    # 订单信息
    waste_weight: Optional[float] = None
    actual_pickup_time: Optional[datetime] = None
    delivery_time: Optional[datetime] = None
    
    # 物业管理信息
    property_manager_id: Optional[int] = None
    property_confirm_time: Optional[datetime] = None
    property_notes: Optional[str] = None
    
    # 运输管理信息
    transport_manager_id: Optional[int] = None
    driver_id: Optional[int] = None
    vehicle_plate: Optional[str] = None
    transport_route: Optional[str] = None
    transport_notes: Optional[str] = None
    
    # 处置回收信息
    recycling_manager_id: Optional[int] = None
    recycling_station_id: Optional[int] = None
    recycling_confirm_time: Optional[datetime] = None
    recycling_notes: Optional[str] = None
    
    # 订单状态和时间
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    
    # 费用信息
    price: float
    payment_status: str
    payment_time: Optional[datetime] = None
    
    # 关系字段
    address: Optional[AddressResponse] = None  # 添加地址关系
    
    class Config:
        orm_mode = True