import pytest
import random
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.crud import user, order, property, transport, recycling, address, community
from app.schemas.user import UserCreate
from app.schemas.order import OrderCreate, OrderStatusUpdate
from app.schemas.property import PropertyCreate
from app.schemas.transport import TransportCreate
from app.schemas.recycling import RecyclingCreate
from app.schemas.address import AddressCreate
from app.schemas.community import CommunityCreate
from app.models.user import UserRole
from app.models.order import OrderStatus
from app.models.transport import DriverStatus
from app.models.recycling import RecyclingStatus
from app.core.security import create_access_token

# 辅助函数：创建不同角色的测试用户并返回token
def create_user_with_role(db: Session, role, is_superuser=False):
    random_number = random.randint(1000, 9999)
    username = f"test{role.lower()}_{random_number}"
    
    user_in = UserCreate(
        username=username,
        email=f"{username}@example.com",
        phone=f"1380000{random_number}",
        password="testpassword",
        full_name=f"测试{role.name}用户",
        role=role,
        is_superuser=is_superuser
    )
    db_user = user.create(db, obj_in=user_in)
    access_token = create_access_token(db_user.id)
    return db_user, access_token

# 辅助函数：创建测试地址
def create_test_address(db: Session, user_id: int):
    address_in = AddressCreate(
        address="测试地址",
        community_name="测试小区",
        building_number="1",
        room_number="101",
        contact_name="测试联系人",
        contact_phone="13800001111",
        is_default=True
    )
    return address.create_with_user(db, obj_in=address_in, user_id=user_id)

# ============ 订单API测试 ============

# 测试创建订单
def test_create_order(client: TestClient, db: Session):
    # 创建客户用户
    customer, token = create_user_with_role(db, UserRole.CUSTOMER)
    
    # 创建测试地址
    test_address = create_test_address(db, customer.id)
    
    # 测试创建订单
    order_data = {
        "address_id": test_address.id,
        "waste_type": "建筑垃圾",
        "waste_volume": 2.5
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/orders/", json=order_data, headers=headers)
    assert response.status_code == 201
    order_data = response.json()
    assert order_data["address"]["community_name"] == "测试小区"
    assert order_data["status"] == OrderStatus.PENDING

# 测试非客户用户创建订单（应该被禁止）
def test_create_order_forbidden(client: TestClient, db: Session):
    # 创建物业用户
    property_user, token = create_user_with_role(db, UserRole.PROPERTY)
    
    # 创建测试地址
    test_address = create_test_address(db, property_user.id)
    
    # 测试物业用户创建订单
    order_data = {
        "address_id": test_address.id,
        "waste_type": "建筑垃圾",
        "waste_volume": 2.5
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/orders/", json=order_data, headers=headers)
    assert response.status_code == 403

# 测试获取订单列表
def test_read_orders(client: TestClient, db: Session):
    # 创建客户用户和地址
    customer, token = create_user_with_role(db, UserRole.CUSTOMER)
    test_address = create_test_address(db, customer.id)
    
    # 创建订单
    order_in = OrderCreate(
        address_id=test_address.id,
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
def test_read_order(client: TestClient, db: Session):
    # 创建客户用户和地址
    customer, token = create_user_with_role(db, UserRole.CUSTOMER)
    test_address = create_test_address(db, customer.id)
    
    # 创建订单
    order_in = OrderCreate(
        address_id=test_address.id,
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
    assert order_data["address"]["community_name"] == "测试小区"

# 测试更新订单状态
def test_update_order_status(client: TestClient, db: Session):
    # 创建客户用户和地址
    customer, customer_token = create_user_with_role(db, UserRole.CUSTOMER)
    test_address = create_test_address(db, customer.id)
    
    # 创建订单
    order_in = OrderCreate(
        address_id=test_address.id,
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
def test_create_property(client: TestClient, db: Session):
    # 创建物业用户
    property_user, token = create_user_with_role(db, UserRole.PROPERTY)
    
    # 测试创建物业信息
    property_data = {
        "name": "测试物业",
        "address": "测试地址",
        "contact_name": "测试联系人",
        "contact_phone": "13800001111"
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/properties/", json=property_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == property_data["name"]
    assert data["address"] == property_data["address"]
    assert data["contact_name"] == property_data["contact_name"]
    assert data["contact_phone"] == property_data["contact_phone"]
    assert len(data["property_managers"]) == 1
    assert data["property_managers"][0]["manager_id"] == property_user.id
    assert data["property_managers"][0]["is_primary"] == True

# 测试获取物业列表
def test_read_properties(client: TestClient, db: Session):
    # 创建物业用户和物业信息
    property_user, token = create_user_with_role(db, UserRole.PROPERTY)
    property_in = PropertyCreate(
        name="测试物业",
        address="测试地址",
        contact_name="测试联系人",
        contact_phone="13800001111"
    )
    db_property = property.create_with_manager(db, obj_in=property_in, manager_id=property_user.id)
    
    # 创建社区
    community_in = CommunityCreate(
        name="测试小区",
        address="测试小区地址"
    )
    community.create_with_property(db, obj_in=community_in, property_id=db_property.id)
    
    # 测试获取物业列表
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/properties/", headers=headers)
    assert response.status_code == 200
    properties_data = response.json()
    assert isinstance(properties_data, list)
    assert len(properties_data) > 0
    assert properties_data[0]["name"] == "测试物业"
    assert len(properties_data[0]["property_managers"]) == 1
    assert properties_data[0]["property_managers"][0]["manager_id"] == property_user.id

# 测试获取特定物业信息
def test_read_property(client: TestClient, db: Session):
    # 创建物业用户和物业信息
    property_user, token = create_user_with_role(db, UserRole.PROPERTY)
    property_in = PropertyCreate(
        name="测试物业",
        address="测试地址",
        contact_name="测试联系人",
        contact_phone="13800001111"
    )
    db_property = property.create_with_manager(db, obj_in=property_in, manager_id=property_user.id)
    
    # 创建社区
    community_in = CommunityCreate(
        name="测试小区",
        address="测试小区地址"
    )
    community.create_with_property(db, obj_in=community_in, property_id=db_property.id)
    
    # 测试获取特定物业信息
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/api/v1/properties/{db_property.id}", headers=headers)
    assert response.status_code == 200
    property_data = response.json()
    assert property_data["id"] == db_property.id
    assert property_data["name"] == "测试物业"
    assert len(property_data["property_managers"]) == 1
    assert property_data["property_managers"][0]["manager_id"] == property_user.id

# 测试更新物业信息
def test_update_property(client: TestClient, db: Session):
    # 创建物业用户和物业信息
    property_user, token = create_user_with_role(db, UserRole.PROPERTY)
    property_in = PropertyCreate(
        name="测试物业",
        address="测试地址",
        contact_name="测试联系人",
        contact_phone="13800001111"
    )
    db_property = property.create_with_manager(db, obj_in=property_in, manager_id=property_user.id)
    
    # 创建社区
    community_in = CommunityCreate(
        name="测试小区",
        address="测试小区地址"
    )
    community.create_with_property(db, obj_in=community_in, property_id=db_property.id)
    
    # 测试更新物业信息
    update_data = {
        "name": "更新后的物业",
        "address": "更新后的地址",
        "contact_name": "更新后的联系人",
        "contact_phone": "13800002222"
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(
        f"/api/v1/properties/{db_property.id}",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["address"] == update_data["address"]
    assert data["contact_name"] == update_data["contact_name"]
    assert data["contact_phone"] == update_data["contact_phone"]
    assert len(data["property_managers"]) == 1
    assert data["property_managers"][0]["manager_id"] == property_user.id

# 测试删除物业信息
def test_delete_property(client: TestClient, db: Session):
    # 创建物业用户和物业信息
    property_user, token = create_user_with_role(db, UserRole.PROPERTY)
    property_in = PropertyCreate(
        name="测试物业",
        address="测试地址",
        contact_name="测试联系人",
        contact_phone="13800001111"
    )
    db_property = property.create_with_manager(db, obj_in=property_in, manager_id=property_user.id)
    
    # 创建社区
    community_in = CommunityCreate(
        name="测试小区",
        address="测试小区地址"
    )
    db_community = community.create_with_property(db, obj_in=community_in, property_id=db_property.id)
    
    # 创建管理员用户
    manager, manager_token = create_user_with_role(db, UserRole.ADMIN, is_superuser=True)
    headers = {"Authorization": f"Bearer {token}"}
    # 验证物业管理员存在
    response = client.get(f"/api/v1/properties/{db_property.id}/managers", headers=headers)
    assert response.status_code == 200

    # 测试删除物业信息
    response = client.delete(f"/api/v1/properties/{db_property.id}", headers={"Authorization": f"Bearer {manager_token}"})
    assert response.status_code == 200
    
    # 验证物业已被删除
    response = client.get(f"/api/v1/properties/{db_property.id}", headers=headers)
    assert response.status_code == 404

    # 验证物业管理员已被删除
    response = client.get(f"/api/v1/properties/{db_property.id}/managers", headers=headers)
    assert response.status_code == 404

    # 验证社区已被删除
    response = client.get(f"/api/v1/communities/{db_community.id}", headers=headers)
    assert response.status_code == 404

# 测试添加物业管理员
def test_add_property_manager(client: TestClient, db: Session):
    # 创建主要管理员和物业
    primary_manager_user, primary_token = create_user_with_role(db, UserRole.PROPERTY)
    property_in = PropertyCreate(
        name="测试物业_add_pm",
        address="测试地址_add_pm",
        contact_name="测试联系人",
        contact_phone="13800001112"
    )
    db_property = property.create_with_manager(db, obj_in=property_in, manager_id=primary_manager_user.id)
    
    # 创建一个小区用于关联
    community_in = CommunityCreate(name="测试小区_add_pm", address="测试小区地址_add_pm")
    db_community = community.create_with_property(db, obj_in=community_in, property_id=db_property.id)

    # 创建新的普通管理员用户
    new_ordinary_manager_user, _ = create_user_with_role(db, UserRole.PROPERTY, is_superuser=False)
    
    # 测试添加普通管理员，关联小区
    manager_data = {
        "manager_id": new_ordinary_manager_user.id,
        "role": "普通管理员",
        "is_primary": False,
        "community_id": db_community.id  # 添加 community_id
    }
    headers = {"Authorization": f"Bearer {primary_token}"}
    response = client.post(
        f"/api/v1/properties/{db_property.id}/managers",
        json=manager_data,
        headers=headers
    )
    assert response.status_code == 200, response.json()
    data = response.json()
    assert data["manager_id"] == new_ordinary_manager_user.id
    assert data["role"] == "普通管理员"
    assert not data["is_primary"]
    assert data["community_id"] == db_community.id
    assert data["community"] is not None
    assert data["community"]["id"] == db_community.id

# 测试更新物业管理员
def test_update_property_manager(client: TestClient, db: Session):
    # 创建主要管理员和物业
    primary_manager_user, primary_token = create_user_with_role(db, UserRole.PROPERTY)
    property_in = PropertyCreate(
        name="测试物业_upd_pm",
        address="测试地址_upd_pm",
        contact_name="测试联系人",
        contact_phone="13800001113",
    )
    db_property = property.create_with_manager(db, obj_in=property_in, manager_id=primary_manager_user.id)
    
    # 创建一个小区用于关联
    db_community1 = community.create_with_property(db, obj_in=CommunityCreate(name="小区1_upd_pm", address="地址1"), property_id=db_property.id)
    db_community2 = community.create_with_property(db, obj_in=CommunityCreate(name="小区2_upd_pm", address="地址2"), property_id=db_property.id)

    # 创建新的普通管理员用户并添加
    new_ordinary_manager_user, _ = create_user_with_role(db, UserRole.PROPERTY)
    
    add_manager_data = {
        "manager_id": new_ordinary_manager_user.id,
        "role": "普通管理员",
        "is_primary": False,
        "community_id": db_community1.id # 初始关联小区1
    }
    headers = {"Authorization": f"Bearer {primary_token}"}
    add_response = client.post(
        f"/api/v1/properties/{db_property.id}/managers",
        json=add_manager_data,
        headers=headers
    )
    assert add_response.status_code == 200, add_response.json()
    pm_id_to_update = add_response.json()["id"] # PropertyManager ID
    
    # 测试更新管理员信息，更改角色和关联小区
    update_data = {
        "role": "高级小区管理员",
        "is_primary": False, # 保持非主要
        "community_id": db_community2.id # 更新到小区2
    }
    update_response = client.put(
        f"/api/v1/properties/{db_property.id}/managers/{pm_id_to_update}", # 使用 pm_id
        json=update_data,
        headers=headers
    )
    assert update_response.status_code == 200, update_response.json()
    data = update_response.json()
    assert data["role"] == "高级小区管理员"
    assert data["community_id"] == db_community2.id
    assert data["community"]["id"] == db_community2.id

# 测试移除物业管理员
def test_remove_property_manager(client: TestClient, db: Session):
    # 创建主要管理员和物业
    primary_manager_user, primary_token = create_user_with_role(db, UserRole.PROPERTY)
    property_in = PropertyCreate(
        name="测试物业_rem_pm",
        address="测试地址_rem_pm",
        contact_name="测试联系人",
        contact_phone="13800001114",
    )
    db_property = property.create_with_manager(db, obj_in=property_in, manager_id=primary_manager_user.id)

    # 创建一个小区用于关联
    db_community = community.create_with_property(db, obj_in=CommunityCreate(name="小区_rem_pm", address="地址_rem_pm"), property_id=db_property.id)
    
    # 创建新的普通管理员用户并添加
    new_ordinary_manager_user, _ = create_user_with_role(db, UserRole.PROPERTY)
    
    add_manager_data = {
        "manager_id": new_ordinary_manager_user.id,
        "role": "待移除管理员",
        "is_primary": False,
        "community_id": db_community.id # 关联小区
    }
    headers = {"Authorization": f"Bearer {primary_token}"}
    add_response = client.post(
        f"/api/v1/properties/{db_property.id}/managers",
        json=add_manager_data,
        headers=headers
    )
    assert add_response.status_code == 200, add_response.json()
    pm_id_to_remove = add_response.json()["id"] # PropertyManager ID
    
    # 测试移除管理员
    remove_response = client.delete(
        f"/api/v1/properties/{db_property.id}/managers/{pm_id_to_remove}", # 使用 pm_id
        headers=headers
    )
    assert remove_response.status_code == 200, remove_response.json()

# ============ 运输API测试 ============

# 测试创建运输信息
def test_create_transport(client: TestClient, db: Session):
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
def test_read_transports(client: TestClient, db: Session):
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
def test_update_driver_status(client: TestClient, db: Session):
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
    status_update = {
        "status": DriverStatus.BUSY
    }
    # 测试更新司机状态
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(f"/api/v1/transports/{db_transport.id}/status", json=status_update, headers=headers)
    assert response.status_code == 200
    transport_data = response.json()
    assert transport_data["driver_status"] == DriverStatus.BUSY

# ============ 回收站API测试 ============

# 测试创建回收站信息
def test_create_recycling(client: TestClient, db: Session):
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
def test_read_recyclings(client: TestClient, db: Session):
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
def test_update_recycling_status(client: TestClient, db: Session):
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
    status_update = {
        "status": RecyclingStatus.MAINTENANCE
    }
    response = client.put(f"/api/v1/recyclings/{db_recycling.id}/status", json=status_update, headers=headers)
    assert response.status_code == 200
    recycling_data = response.json()
    assert recycling_data["status"] == RecyclingStatus.MAINTENANCE