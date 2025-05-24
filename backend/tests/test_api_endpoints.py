import pytest
import random
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.crud import user, order, property as crud_property_module, transport, recycling, address, community as crud_community_module
from app.crud.crud_property_manager import property_manager as crud_prop_manager
from app.schemas.user import UserCreate
from app.schemas.order import OrderCreate, OrderStatusUpdate
from app.schemas.property import PropertyCreate
from app.schemas.property_manager import PropertyManagerCreate
from app.schemas.transport import TransportCreate
from app.schemas.recycling import RecyclingCreate
from app.schemas.address import AddressCreate
from app.schemas.community import CommunityCreate
from app.models.user import User, UserRole
from app.models.order import OrderStatus
from app.models.transport import DriverStatus
from app.models.recycling import RecyclingStatus
from app.models.property import Property
from app.models.community import Community
from app.core.security import create_access_token

# 辅助函数：创建不同角色的测试用户并返回token
def create_user_with_role(db: Session, role: UserRole, is_superuser=False) -> tuple[User, str]:
    random_number = random.randint(10000, 19999)
    username = f"test_{role.value.lower()}_{random_number}"
    
    user_in = UserCreate(
        username=username,
        email=f"{username}@example.com",
        phone=f"138100{random_number}",
        password="testpassword",
        full_name=f"测试 {role.name} 用户",
        role=role,
        is_superuser=is_superuser
    )
    db_user = user.create(db, obj_in=user_in)
    access_token = create_access_token(db_user.id)
    return db_user, access_token

# 辅助函数：创建测试物业和小区 (因为地址和小区强相关)
def create_test_property_and_community(db: Session, manager_user: User) -> tuple[Property, Community]:
    prop_in = PropertyCreate(
        name=f"测试物业_{random.randint(1000,9999)}", 
        address=f"测试物业地址_{random.randint(1000,9999)}",
        contact_name="物业联系人",
        contact_phone="13700008888"
    )
    test_prop = crud_property_module.create_with_manager(db, obj_in=prop_in, manager_id=manager_user.id)
    
    community_in = CommunityCreate(
        name=f"测试小区_{random.randint(1000,9999)}",
        address=f"测试小区地址_{random.randint(1000,9999)}",
    )
    test_community = crud_community_module.create_with_property(db, obj_in=community_in, property_id=test_prop.id)
    return test_prop, test_community

# 辅助函数：创建测试地址 (需要 community_id)
def create_test_address(db: Session, user_id: int, community_id: int, suffix: str = ""):
    address_in = AddressCreate(
        address=f"测试街道_{suffix}",
        community_id=community_id,
        building_number=f"B{random.randint(1,10)}{suffix}",
        room_number=f"R{random.randint(100,199)}{suffix}",
        contact_name=f"联系人_{suffix}",
        contact_phone=f"1390000{random.randint(1000,1999)}",
        is_default=True
    )
    return address.create_with_user(db, obj_in=address_in, user_id=user_id)

# ============ 订单API测试 ============

# 测试创建订单
def test_create_order(client: TestClient, db: Session):
    # 创建物业用户 (用于创建物业和小区)
    prop_manager_user, _ = create_user_with_role(db, UserRole.PROPERTY)
    _, test_community = create_test_property_and_community(db, manager_user=prop_manager_user)

    # 创建客户用户
    customer_user, token = create_user_with_role(db, UserRole.CUSTOMER)
    
    # 创建测试地址 (关联到小区)
    test_address = create_test_address(db, customer_user.id, test_community.id, suffix="_create_order")
    
    order_data_in = {
        "address_id": test_address.id,
        "waste_type": "建筑垃圾 From Create Order Test",
        "waste_volume": 2.5
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/orders/", json=order_data_in, headers=headers)
    assert response.status_code == 201, response.text
    order_data_out = response.json()
    assert order_data_out["address"]["community_id"] == test_community.id
    assert order_data_out["address"]["community"]["name"] == test_community.name
    assert order_data_out["status"] == OrderStatus.PENDING.value

# 测试非客户用户创建订单（应该被禁止）
def test_create_order_forbidden(client: TestClient, db: Session):
    prop_user_for_addr, _ = create_user_with_role(db, UserRole.PROPERTY)
    _, community_for_addr = create_test_property_and_community(db, prop_user_for_addr)

    # 创建物业用户 (试图创建订单的用户)
    property_user_trying, token = create_user_with_role(db, UserRole.PROPERTY)
    
    # 创建测试地址 (可以属于 property_user_trying 或其他用户，但订单创建者是关键)
    test_address_forbidden = create_test_address(db, property_user_trying.id, community_for_addr.id, suffix="_forbidden")
    
    order_data = {
        "address_id": test_address_forbidden.id,
        "waste_type": "建筑垃圾",
        "waste_volume": 2.5
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/orders/", json=order_data, headers=headers)
    assert response.status_code == 403, response.text

# 测试获取订单列表 (客户视角)
def test_read_orders_as_customer(client: TestClient, db: Session):
    # 1. 设置基础环境: 物业、小区
    prop_mgr_user_owner, prop_mgr_owner_token = create_user_with_role(db, UserRole.PROPERTY) # This user will own the property
    test_property, test_community = create_test_property_and_community(db, manager_user=prop_mgr_user_owner)
    
    # 2. 创建客户和客户的地址
    customer_user, customer_token = create_user_with_role(db, UserRole.CUSTOMER)
    test_address = create_test_address(db, user_id=customer_user.id, community_id=test_community.id, suffix="_read_cust")
    
    # 3. 客户创建两个订单 (初始都为 PENDING)
    order1_pending = order.create_with_customer(db, obj_in=OrderCreate(address_id=test_address.id, waste_type="T1 PENDING", waste_volume=1), customer_id=customer_user.id)
    order2_to_be_confirmed = order.create_with_customer(db, obj_in=OrderCreate(address_id=test_address.id, waste_type="T2 TO_BE_CONFIRMED", waste_volume=2), customer_id=customer_user.id)

    # 4. 物业管理员确认其中一个订单
    # prop_mgr_user_owner is the primary manager of test_property, so they can confirm orders in test_community.
    confirm_payload = {"status": OrderStatus.PROPERTY_CONFIRMED.value}
    confirm_headers = {"Authorization": f"Bearer {prop_mgr_owner_token}"}
    response_confirm = client.put(f"/api/v1/orders/{order2_to_be_confirmed.id}/status", json=confirm_payload, headers=confirm_headers)
    assert response_confirm.status_code == 200, f"Failed to confirm order: {response_confirm.text}"
    confirmed_order_data = response_confirm.json()
    assert confirmed_order_data["status"] == OrderStatus.PROPERTY_CONFIRMED.value
    assert confirmed_order_data["property_manager_id"] == prop_mgr_user_owner.id

    # 5. 客户获取自己的订单列表
    cust_headers = {"Authorization": f"Bearer {customer_token}"}
    response_all = client.get("/api/v1/orders/", headers=cust_headers)
    assert response_all.status_code == 200, response_all.text
    orders_data = response_all.json()
    assert isinstance(orders_data, list)
    assert len(orders_data) == 2 # Should get both orders
    
    # Verify one order is PENDING and the other is PROPERTY_CONFIRMED by checking their IDs and statuses
    found_pending = False
    found_confirmed = False
    for o_data in orders_data:
        if o_data["id"] == order1_pending.id:
            assert o_data["status"] == OrderStatus.PENDING.value
            found_pending = True
        elif o_data["id"] == order2_to_be_confirmed.id:
            assert o_data["status"] == OrderStatus.PROPERTY_CONFIRMED.value
            found_confirmed = True
        assert o_data["address"]["community_id"] == test_community.id # Check community info consistency
    assert found_pending and found_confirmed, "Did not find both pending and confirmed orders for customer"

    # 6. 测试状态过滤 (客户视角)
    response_pending_filter = client.get("/api/v1/orders/?status=pending", headers=cust_headers)
    assert response_pending_filter.status_code == 200, response_pending_filter.text
    pending_orders_data = response_pending_filter.json()
    assert len(pending_orders_data) == 1
    assert pending_orders_data[0]["id"] == order1_pending.id
    assert pending_orders_data[0]["status"] == OrderStatus.PENDING.value

    response_confirmed_filter = client.get("/api/v1/orders/?status=property_confirmed", headers=cust_headers)
    assert response_confirmed_filter.status_code == 200, response_confirmed_filter.text
    confirmed_orders_data = response_confirmed_filter.json()
    assert len(confirmed_orders_data) == 1
    assert confirmed_orders_data[0]["id"] == order2_to_be_confirmed.id
    assert confirmed_orders_data[0]["status"] == OrderStatus.PROPERTY_CONFIRMED.value

def test_read_orders_as_property_manager(client: TestClient, db: Session):
    # Setup: Property, CommunityA, CommunityB
    primary_mgr_user, primary_token = create_user_with_role(db, UserRole.PROPERTY, is_superuser=False)
    test_prop, community_A = create_test_property_and_community(db, manager_user=primary_mgr_user)
    community_B = crud_community_module.create_with_property(db, obj_in=CommunityCreate(name=f"Comm B_{random.randint(100,199)}", address="Addr B"), property_id=test_prop.id)

    # Normal manager for Community A
    normal_mgr_A_user, normal_mgr_A_token = create_user_with_role(db, UserRole.PROPERTY)
    crud_prop_manager.create(db, obj_in=PropertyManagerCreate(manager_id=normal_mgr_A_user.id, role="Normal A", is_primary=False, community_id=community_A.id), property_id=test_prop.id)

    # Customer and orders
    customer, _ = create_user_with_role(db, UserRole.CUSTOMER)
    addr_A1 = create_test_address(db, customer.id, community_A.id, "_RA1")
    ord_A1 = order.create_with_customer(db, obj_in=OrderCreate(address_id=addr_A1.id, waste_type="CA1", waste_volume=1), customer_id=customer.id)
    addr_A2 = create_test_address(db, customer.id, community_A.id, "_RA2")
    ord_A2 = order.create_with_customer(db, obj_in=OrderCreate(address_id=addr_A2.id, waste_type="CA2", waste_volume=1), customer_id=customer.id)
    addr_B1 = create_test_address(db, customer.id, community_B.id, "_RB1")
    ord_B1 = order.create_with_customer(db, obj_in=OrderCreate(address_id=addr_B1.id, waste_type="CB1", waste_volume=1), customer_id=customer.id)

    # Primary manager should see all 3 orders
    headers_primary = {"Authorization": f"Bearer {primary_token}"}
    response_primary = client.get("/api/v1/orders/", headers=headers_primary)
    assert response_primary.status_code == 200, response_primary.text
    primary_orders = {o["id"] for o in response_primary.json()}
    assert primary_orders == {ord_A1.id, ord_A2.id, ord_B1.id}

    # Normal manager A should see 2 orders from Community A
    headers_normal_A = {"Authorization": f"Bearer {normal_mgr_A_token}"}
    response_normal_A = client.get("/api/v1/orders/", headers=headers_normal_A)
    assert response_normal_A.status_code == 200, response_normal_A.text
    normal_A_orders = {o["id"] for o in response_normal_A.json()}
    assert normal_A_orders == {ord_A1.id, ord_A2.id}

    # Create a manager for another property, should see 0 of these orders
    other_prop_mgr_user, other_token = create_user_with_role(db, UserRole.PROPERTY)
    create_test_property_and_community(db, manager_user=other_prop_mgr_user) # Creates unrelated property & community
    headers_other = {"Authorization": f"Bearer {other_token}"}
    response_other = client.get("/api/v1/orders/", headers=headers_other)
    assert response_other.status_code == 200, response_other.text
    assert len(response_other.json()) == 0

# 测试获取特定订单
def test_read_order(client: TestClient, db: Session):
    primary_mgr_user, primary_token = create_user_with_role(db, UserRole.PROPERTY)
    test_prop, community_A = create_test_property_and_community(db, manager_user=primary_mgr_user)
    community_B = crud_community_module.create_with_property(db, obj_in=CommunityCreate(name=f"Comm B_{random.randint(200,299)}", address="Addr B Read"), property_id=test_prop.id)

    normal_mgr_A_user, normal_mgr_A_token = create_user_with_role(db, UserRole.PROPERTY)
    crud_prop_manager.create(db, obj_in=PropertyManagerCreate(manager_id=normal_mgr_A_user.id, role="Normal A Read", is_primary=False, community_id=community_A.id), property_id=test_prop.id)

    customer_user, customer_token = create_user_with_role(db, UserRole.CUSTOMER)
    addr_A = create_test_address(db, customer_user.id, community_A.id, "_ReadOrdA")
    ord_A = order.create_with_customer(db, obj_in=OrderCreate(address_id=addr_A.id, waste_type="ReadA", waste_volume=1), customer_id=customer_user.id)
    addr_B = create_test_address(db, customer_user.id, community_B.id, "_ReadOrdB")
    ord_B = order.create_with_customer(db, obj_in=OrderCreate(address_id=addr_B.id, waste_type="ReadB", waste_volume=1), customer_id=customer_user.id)

    # Customer can read their own order
    response_cust = client.get(f"/api/v1/orders/{ord_A.id}", headers={"Authorization": f"Bearer {customer_token}"})
    assert response_cust.status_code == 200, response_cust.text
    assert response_cust.json()["id"] == ord_A.id

    # Primary manager can read order in Community A and B
    response_primary_A = client.get(f"/api/v1/orders/{ord_A.id}", headers={"Authorization": f"Bearer {primary_token}"})
    assert response_primary_A.status_code == 200, response_primary_A.text
    response_primary_B = client.get(f"/api/v1/orders/{ord_B.id}", headers={"Authorization": f"Bearer {primary_token}"})
    assert response_primary_B.status_code == 200, response_primary_B.text

    # Normal manager A can read order in Community A
    response_normal_A_CanRead = client.get(f"/api/v1/orders/{ord_A.id}", headers={"Authorization": f"Bearer {normal_mgr_A_token}"})
    assert response_normal_A_CanRead.status_code == 200, response_normal_A_CanRead.text

    # Normal manager A CANNOT read order in Community B
    response_normal_A_CannotRead = client.get(f"/api/v1/orders/{ord_B.id}", headers={"Authorization": f"Bearer {normal_mgr_A_token}"})
    assert response_normal_A_CannotRead.status_code == 403, response_normal_A_CannotRead.text

# 测试更新订单状态
def test_update_order_status(client: TestClient, db: Session):
    primary_mgr_user, primary_token = create_user_with_role(db, UserRole.PROPERTY)
    test_prop, community_A = create_test_property_and_community(db, manager_user=primary_mgr_user)
    community_B = crud_community_module.create_with_property(db, obj_in=CommunityCreate(name=f"Comm B_{random.randint(300,399)}", address="Addr B Update"), property_id=test_prop.id)

    normal_mgr_A_user, normal_mgr_A_token = create_user_with_role(db, UserRole.PROPERTY)
    crud_prop_manager.create(db, obj_in=PropertyManagerCreate(manager_id=normal_mgr_A_user.id, role="Normal A Update", is_primary=False, community_id=community_A.id), property_id=test_prop.id)

    customer_user, _ = create_user_with_role(db, UserRole.CUSTOMER)
    addr_A = create_test_address(db, customer_user.id, community_A.id, "_UpdOrdA")
    ord_A_pending = order.create_with_customer(db, obj_in=OrderCreate(address_id=addr_A.id, waste_type="PendingA", waste_volume=1), customer_id=customer_user.id)
    
    addr_B = create_test_address(db, customer_user.id, community_B.id, "_UpdOrdB")
    ord_B_pending = order.create_with_customer(db, obj_in=OrderCreate(address_id=addr_B.id, waste_type="PendingB", waste_volume=1), customer_id=customer_user.id)

    status_update_payload = {"status": OrderStatus.PROPERTY_CONFIRMED.value}

    # Primary manager confirms order in Community A
    response_primary_confirms_A = client.put(f"/api/v1/orders/{ord_A_pending.id}/status", json=status_update_payload, headers={"Authorization": f"Bearer {primary_token}"})
    assert response_primary_confirms_A.status_code == 200, response_primary_confirms_A.text
    data_primary_A = response_primary_confirms_A.json()
    assert data_primary_A["status"] == OrderStatus.PROPERTY_CONFIRMED.value
    assert data_primary_A["property_manager_id"] == primary_mgr_user.id
    assert data_primary_A["property_confirm_time"] is not None
    assert data_primary_A["address"]["community_id"] == community_A.id

    # Normal manager A confirms order in Community A (ord_A_pending was already confirmed, let's use a new one or reset)
    # Recreate a pending order in A for normal_mgr_A to confirm
    ord_A_pending_for_normal = order.create_with_customer(db, obj_in=OrderCreate(address_id=addr_A.id, waste_type="PendingA Normal", waste_volume=1), customer_id=customer_user.id)
    response_normal_A_confirms_A = client.put(f"/api/v1/orders/{ord_A_pending_for_normal.id}/status", json=status_update_payload, headers={"Authorization": f"Bearer {normal_mgr_A_token}"})
    assert response_normal_A_confirms_A.status_code == 200, response_normal_A_confirms_A.text
    data_normal_A = response_normal_A_confirms_A.json()
    assert data_normal_A["status"] == OrderStatus.PROPERTY_CONFIRMED.value
    assert data_normal_A["property_manager_id"] == normal_mgr_A_user.id

    # Normal manager A CANNOT confirm order in Community B
    response_normal_A_confirms_B = client.put(f"/api/v1/orders/{ord_B_pending.id}/status", json=status_update_payload, headers={"Authorization": f"Bearer {normal_mgr_A_token}"})
    assert response_normal_A_confirms_B.status_code == 403, response_normal_A_confirms_B.text # Expecting 403 due to community permission

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
    db_property = crud_property_module.create_with_manager(db, obj_in=property_in, manager_id=property_user.id)
    
    # 创建社区
    community_in = CommunityCreate(
        name="测试小区",
        address="测试小区地址"
    )
    crud_community_module.create_with_property(db, obj_in=community_in, property_id=db_property.id)
    
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
    db_property = crud_property_module.create_with_manager(db, obj_in=property_in, manager_id=property_user.id)
    
    # 创建社区
    community_in = CommunityCreate(
        name="测试小区",
        address="测试小区地址"
    )
    crud_community_module.create_with_property(db, obj_in=community_in, property_id=db_property.id)
    
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
    db_property = crud_property_module.create_with_manager(db, obj_in=property_in, manager_id=property_user.id)
    
    # 创建社区
    community_in = CommunityCreate(
        name="测试小区",
        address="测试小区地址"
    )
    crud_community_module.create_with_property(db, obj_in=community_in, property_id=db_property.id)
    
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
    db_property = crud_property_module.create_with_manager(db, obj_in=property_in, manager_id=property_user.id)
    
    # 创建社区
    community_in = CommunityCreate(
        name="测试小区",
        address="测试小区地址"
    )
    db_community = crud_community_module.create_with_property(db, obj_in=community_in, property_id=db_property.id)
    
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
    db_property = crud_property_module.create_with_manager(db, obj_in=property_in, manager_id=primary_manager_user.id)
    
    # 创建一个小区用于关联
    community_in = CommunityCreate(name="测试小区_add_pm", address="测试小区地址_add_pm")
    db_community = crud_community_module.create_with_property(db, obj_in=community_in, property_id=db_property.id)

    # 创建新的普通管理员用户
    new_ordinary_manager_user, _ = create_user_with_role(db, UserRole.PROPERTY, is_superuser=False)
    
    # 测试添加普通管理员，关联小区
    manager_data = {
        "manager_id": new_ordinary_manager_user.id,
        "role": "普通管理员",
        "is_primary": False,
        "community_id": db_community.id
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
    db_property = crud_property_module.create_with_manager(db, obj_in=property_in, manager_id=primary_manager_user.id)
    
    # 创建一个小区用于关联
    db_community1 = crud_community_module.create_with_property(db, obj_in=CommunityCreate(name="小区1_upd_pm", address="地址1"), property_id=db_property.id)
    db_community2 = crud_community_module.create_with_property(db, obj_in=CommunityCreate(name="小区2_upd_pm", address="地址2"), property_id=db_property.id)

    # 创建新的普通管理员用户并添加
    new_ordinary_manager_user, _ = create_user_with_role(db, UserRole.PROPERTY)
    
    add_manager_data = {
        "manager_id": new_ordinary_manager_user.id,
        "role": "普通管理员",
        "is_primary": False,
        "community_id": db_community1.id
    }
    headers = {"Authorization": f"Bearer {primary_token}"}
    add_response = client.post(
        f"/api/v1/properties/{db_property.id}/managers",
        json=add_manager_data,
        headers=headers
    )
    assert add_response.status_code == 200, add_response.json()
    pm_id_to_update = add_response.json()["id"]
    
    # 测试更新管理员信息，更改角色和关联小区
    update_data = {
        "role": "高级小区管理员",
        "is_primary": False,
        "community_id": db_community2.id
    }
    update_response = client.put(
        f"/api/v1/properties/{db_property.id}/managers/{pm_id_to_update}",
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
    db_property = crud_property_module.create_with_manager(db, obj_in=property_in, manager_id=primary_manager_user.id)

    # 创建一个小区用于关联
    db_community = crud_community_module.create_with_property(db, obj_in=CommunityCreate(name="小区_rem_pm", address="地址_rem_pm"), property_id=db_property.id)
    
    # 创建新的普通管理员用户并添加
    new_ordinary_manager_user, _ = create_user_with_role(db, UserRole.PROPERTY)
    
    add_manager_data = {
        "manager_id": new_ordinary_manager_user.id,
        "role": "待移除管理员",
        "is_primary": False,
        "community_id": db_community.id
    }
    headers = {"Authorization": f"Bearer {primary_token}"}
    add_response = client.post(
        f"/api/v1/properties/{db_property.id}/managers",
        json=add_manager_data,
        headers=headers
    )
    assert add_response.status_code == 200, add_response.json()
    pm_id_to_remove = add_response.json()["id"]
    
    # 测试移除管理员
    remove_response = client.delete(
        f"/api/v1/properties/{db_property.id}/managers/{pm_id_to_remove}",
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