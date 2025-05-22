import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from app.crud import user, order, property, transport, recycling
from app.schemas.user import UserCreate
from app.schemas.order import OrderCreate, OrderStatusUpdate
from app.schemas.property import PropertyCreate
from app.schemas.transport import TransportCreate
from app.schemas.recycling import RecyclingCreate
from app.models.user import UserRole
from app.models.order import OrderStatus
from app.models.transport import DriverStatus
from app.models.recycling import RecyclingStatus
from app.core.security import create_access_token

client = TestClient(app)

# 辅助函数：创建不同角色的测试用户并返回token
def create_user_with_role(db: Session, role, is_superuser=False):
    username = f"test{role.lower()}"
    user_in = UserCreate(
        username=username,
        email=f"{username}@example.com",
        phone=f"1380000{role.value}",
        password="testpassword",
        full_name=f"测试{role.name}用户",
        role=role,
        is_superuser=is_superuser
    )
    db_user = user.create(db, obj_in=user_in)
    access_token = create_access_token(db_user.id)
    return db_user, access_token

# ============ 订单API测试 ============

# 测试创建订单
def test_create_order(db: Session):
    # 创建客户用户
    customer, token = create_user_with_role(db, UserRole.CUSTOMER)
    
    # 测试创建订单
    order_data = {
        "customer_address": "测试地址",
        "community_name": "测试小区",
        "building_number": "1",
        "room_number": "101",
        "contact_name": "测试联系人",
        "contact_phone": "13800001111",
        "waste_type": "建筑垃圾",
        "waste_volume": 2.5
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/orders/", json=order_data, headers=headers)
    assert response.status_code == 201
    order_data = response.json()
    assert order_data["community_name"] == "测试小区"
    assert order_data["status"] == OrderStatus.PENDING

# 测试非客户用户创建订单（应该被禁止）
def test_create_order_forbidden(db: Session):
    # 创建物业用户
    property_user, token = create_user_with_role(db, UserRole.PROPERTY)
    
    # 测试物业用户创建订单
    order_data = {
        "customer_address": "测试地址",
        "community_name": "测试小区",
        "building_number": "1",
        "room_number": "101",
        "contact_name": "测试联系人",
        "contact_phone": "13800001111",
        "waste_type": "建筑垃圾",
        "waste_volume": 2.5
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/orders/", json=order_data, headers=headers)
    assert response.status_code == 403

# 测试获取订单列表
def test_read_orders(db: Session):
    # 创建客户用户和订单
    customer, token = create_user_with_role(db, UserRole.CUSTOMER)
    order_in = OrderCreate(
        customer_address="测试地址",
        community_name="测试小区",
        building_number="1",
        room_number="101",
        contact_name="测试联系人",
        contact_phone="13800001111",
        waste_type="建筑垃圾",
        waste_volume=2.5
    )
    db_order = order.create_with_customer(db, obj_in=order_in, customer_id=customer.id)
    
    # 测试获取订单列表
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/orders/", headers=headers)
    assert response.status_code == 200
    orders_data = response.json()
    assert isinstance(orders_data, list)
    assert len(orders_data) > 0

# 测试获取特定订单
def test_read_order(db: Session):
    # 创建客户用户和订单
    customer, token = create_user_with_role(db, UserRole.CUSTOMER)
    order_in = OrderCreate(
        customer_address="测试地址",
        community_name="测试小区",
        building_number="1",
        room_number="101",
        contact_name="测试联系人",
        contact_phone="13800001111",
        waste_type="建筑垃圾",
        waste_volume=2.5
    )
    db_order = order.create_with_customer(db, obj_in=order_in, customer_id=customer.id)
    
    # 测试获取特定订单
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/api/v1/orders/{db_order.id}", headers=headers)
    assert response.status_code == 200
    order_data = response.json()
    assert order_data["id"] == db_order.id
    assert order_data["community_name"] == "测试小区"

# 测试更新订单状态
def test_update_order_status(db: Session):
    # 创建客户用户和订单
    customer, customer_token = create_user_with_role(db, UserRole.CUSTOMER)
    order_in = OrderCreate(
        customer_address="测试地址",
        community_name="测试小区",
        building_number="1",
        room_number="101",
        contact_name="测试联系人",
        contact_phone="13800001111",
        waste_type="建筑垃圾",
        waste_volume=2.5
    )
    db_order = order.create_with_customer(db, obj_in=order_in, customer_id=customer.id)
    
    # 创建物业用户
    property_user, property_token = create_user_with_role(db, UserRole.PROPERTY)
    
    # 测试物业用户更新订单状态
    status_update = {
        "status": OrderStatus.PROPERTY_CONFIRMED
    }
    headers = {"Authorization": f"Bearer {property_token}"}
    response = client.put(f"/api/v1/orders/{db_order.id}/status", json=status_update, headers=headers)
    assert response.status_code == 200
    order_data = response.json()
    assert order_data["status"] == OrderStatus.PROPERTY_CONFIRMED

# ============ 物业API测试 ============

# 测试创建物业信息
def test_create_property(db: Session):
    # 创建物业用户
    property_user, token = create_user_with_role(db, UserRole.PROPERTY)
    
    # 测试创建物业信息
    property_data = {
        "name": "测试物业",
        "address": "测试地址",
        "contact_name": "测试联系人",
        "contact_phone": "13800001111",
        "community_name": "测试小区"
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/properties/", json=property_data, headers=headers)
    assert response.status_code == 201
    property_data = response.json()
    assert property_data["name"] == "测试物业"
    assert property_data["community_name"] == "测试小区"

# 测试获取物业列表
def test_read_properties(db: Session):
    # 创建物业用户和物业信息
    property_user, token = create_user_with_role(db, UserRole.PROPERTY)
    property_in = PropertyCreate(
        name="测试物业",
        address="测试地址",
        contact_name="测试联系人",
        contact_phone="13800001111",
        community_name="测试小区"
    )
    db_property = property.create_with_manager(db, obj_in=property_in, manager_id=property_user.id)
    
    # 测试获取物业列表
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/properties/", headers=headers)
    assert response.status_code == 200
    properties_data = response.json()
    assert isinstance(properties_data, list)
    assert len(properties_data) > 0

# 测试获取特定物业信息
def test_read_property(db: Session):
    # 创建物业用户和物业信息
    property_user, token = create_user_with_role(db, UserRole.PROPERTY)
    property_in = PropertyCreate(
        name="测试物业",
        address="测试地址",
        contact_name="测试联系人",
        contact_phone="13800001111",
        community_name="测试小区"
    )
    db_property = property.create_with_manager(db, obj_in=property_in, manager_id=property_user.id)
    
    # 测试获取特定物业信息
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/api/v1/properties/{db_property.id}", headers=headers)
    assert response.status_code == 200
    property_data = response.json()
    assert property_data["id"] == db_property.id
    assert property_data["name"] == "测试物业"

# ============ 运输API测试 ============

# 测试创建运输信息
def test_create_transport(db: Session):
    # 创建运输用户
    transport_user, token = create_user_with_role(db, UserRole.TRANSPORT)
    
    # 测试创建运输信息
    transport_data = {
        "driver_name": "测试司机",
        "driver_phone": "13800002222",
        "driver_license": "123456789",
        "vehicle_plate": "京A12345",
        "vehicle_capacity": 10.0,
        "vehicle_volume": 20.0
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/transports/", json=transport_data, headers=headers)
    assert response.status_code == 201
    transport_data = response.json()
    assert transport_data["driver_name"] == "测试司机"
    assert transport_data["vehicle_plate"] == "京A12345"

# 测试获取运输列表
def test_read_transports(db: Session):
    # 创建运输用户和运输信息
    transport_user, token = create_user_with_role(db, UserRole.TRANSPORT)
    transport_in = TransportCreate(
        driver_name="测试司机",
        driver_phone="13800002222",
        driver_license="123456789",
        vehicle_plate="京A12345",
        vehicle_capacity=10.0,
        vehicle_volume=20.0
    )
    db_transport = transport.create_with_manager(db, obj_in=transport_in, manager_id=transport_user.id)
    
    # 测试获取运输列表
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/transports/", headers=headers)
    assert response.status_code == 200
    transports_data = response.json()
    assert isinstance(transports_data, list)
    assert len(transports_data) > 0

# 测试更新司机状态
def test_update_driver_status(db: Session):
    # 创建运输用户和运输信息
    transport_user, token = create_user_with_role(db, UserRole.TRANSPORT)
    transport_in = TransportCreate(
        driver_name="测试司机",
        driver_phone="13800002222",
        driver_license="123456789",
        vehicle_plate="京A12345",
        vehicle_capacity=10.0,
        vehicle_volume=20.0
    )
    db_transport = transport.create_with_manager(db, obj_in=transport_in, manager_id=transport_user.id)
    
    # 测试更新司机状态
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(f"/api/v1/transports/{db_transport.id}/status?status={DriverStatus.BUSY}", headers=headers)
    assert response.status_code == 200
    transport_data = response.json()
    assert transport_data["driver_status"] == DriverStatus.BUSY

# ============ 回收站API测试 ============

# 测试创建回收站信息
def test_create_recycling(db: Session):
    # 创建回收站用户
    recycling_user, token = create_user_with_role(db, UserRole.RECYCLING)
    
    # 测试创建回收站信息
    recycling_data = {
        "name": "测试回收站",
        "address": "测试地址",
        "contact_name": "测试联系人",
        "contact_phone": "13800003333",
        "capacity": 100.0
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/recyclings/", json=recycling_data, headers=headers)
    assert response.status_code == 201
    recycling_data = response.json()
    assert recycling_data["name"] == "测试回收站"
    assert recycling_data["capacity"] == 100.0

# 测试获取回收站列表
def test_read_recyclings(db: Session):
    # 创建回收站用户和回收站信息
    recycling_user, token = create_user_with_role(db, UserRole.RECYCLING)
    recycling_in = RecyclingCreate(
        name="测试回收站",
        address="测试地址",
        contact_name="测试联系人",
        contact_phone="13800003333",
        capacity=100.0
    )
    db_recycling = recycling.create_with_manager(db, obj_in=recycling_in, manager_id=recycling_user.id)
    
    # 测试获取回收站列表
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/recyclings/", headers=headers)
    assert response.status_code == 200
    recyclings_data = response.json()
    assert isinstance(recyclings_data, list)
    assert len(recyclings_data) > 0

# 测试更新回收站状态
def test_update_recycling_status(db: Session):
    # 创建回收站用户和回收站信息
    recycling_user, token = create_user_with_role(db, UserRole.RECYCLING)
    recycling_in = RecyclingCreate(
        name="测试回收站",
        address="测试地址",
        contact_name="测试联系人",
        contact_phone="13800003333",
        capacity=100.0
    )
    db_recycling = recycling.create_with_manager(db, obj_in=recycling_in, manager_id=recycling_user.id)
    
    # 测试更新回收站状态
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(f"/api/v1/recyclings/{db_recycling.id}/status?status={RecyclingStatus.MAINTENANCE}", headers=headers)
    assert response.status_code == 200
    recycling_data = response.json()
    assert recycling_data["status"] == RecyclingStatus.MAINTENANCE