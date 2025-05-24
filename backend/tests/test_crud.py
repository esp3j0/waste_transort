import pytest
from sqlalchemy.orm import Session

from app.crud import user, property as crud_property, order, transport, recycling, address, community as crud_community
from app.crud.crud_property_manager import property_manager as crud_prop_manager
from app.models.user import User, UserRole
from app.models.address import Address
from app.models.order import Order, OrderStatus, RenovationStatus, RenovationType
from app.models.transport import Transport, DriverStatus
from app.models.recycling import Recycling, RecyclingStatus
from app.models.property_manager import PropertyManager
from app.schemas.user import UserCreate
from app.schemas.order import OrderCreate
from app.schemas.transport import TransportCreate
from app.schemas.recycling import RecyclingCreate
from app.schemas.address import AddressCreate
from app.schemas.property import PropertyCreate
from app.schemas.property_manager import PropertyManagerCreate, PropertyManagerUpdate
from app.schemas.community import CommunityCreate
from sqlalchemy.orm import joinedload

# 测试用户CRUD操作
def test_create_user(db: Session):
    user_in = UserCreate(
        username="testuser_crud_user",
        email="test_crud_user@example.com",
        phone="13800001111",
        password="testpassword",
        full_name="测试用户",
        role=UserRole.CUSTOMER
    )
    db_user = user.create(db, obj_in=user_in)
    assert db_user.username == "testuser_crud_user"
    assert db_user.email == "test_crud_user@example.com"
    assert db_user.role == UserRole.CUSTOMER

# 测试地址CRUD操作
def test_create_address(db: Session):
    # 创建测试用户 (物业角色用于创建物业)
    prop_mgr_user_in = UserCreate(
        username="testuser_addr_prop",
        email="test_addr_prop@example.com",
        phone="13800001112",
        password="testpassword",
        full_name="测试物业用户ForAddr",
        role=UserRole.PROPERTY
    )
    db_prop_mgr_user = user.create(db, obj_in=prop_mgr_user_in)

    # 创建测试物业
    property_in_addr = PropertyCreate(
        name="测试物业ForAddr",
        address="测试物业地址ForAddr",
        contact_name="物业联系人ForAddr",
        contact_phone="13800001113"
    )
    db_property_addr = crud_property.create_with_manager(db, obj_in=property_in_addr, manager_id=db_prop_mgr_user.id)

    # 创建测试小区
    community_in_addr = CommunityCreate(
        name="测试小区ForAddr", 
        address="测试小区地址ForAddr",
        # property_id will be set by create_with_property if available, or manually
    )
    # Assuming crud_community.create takes property_id directly or a create_with_property exists
    db_community_addr = crud_community.create_with_property(db, obj_in=community_in_addr, property_id=db_property_addr.id)

    # 创建测试用户 (客户角色用于创建地址)
    cust_user_in = UserCreate(
        username="testuser_addr_cust",
        email="test_addr_cust@example.com",
        phone="13800001114",
        password="testpassword",
        full_name="测试客户ForAddr",
        role=UserRole.CUSTOMER
    )
    db_cust_user = user.create(db, obj_in=cust_user_in)
    
    # 创建测试地址
    address_in = AddressCreate(
        address="测试街道地址123号",
        community_id=db_community_addr.id,
        building_number="栋1",
        room_number="房101",
        contact_name="地址联系人张三",
        contact_phone="13800001115",
        is_default=True
    )
    db_address = address.create_with_user(db, obj_in=address_in, user_id=db_cust_user.id)
    assert db_address.community_id == db_community_addr.id
    assert db_address.community is not None
    assert db_address.community.name == "测试小区ForAddr"
    assert db_address.is_default == True

# 测试订单CRUD操作
def test_create_order(db: Session):
    # 创建测试用户 (物业角色用于创建物业)
    prop_mgr_user_order_in = UserCreate(
        username="testuser_order_prop",
        email="test_order_prop@example.com",
        phone="13800001122", 
        password="testpassword",
        full_name="测试物业用户ForOrder",
        role=UserRole.PROPERTY
    )
    db_prop_mgr_user_order = user.create(db, obj_in=prop_mgr_user_order_in)

    # 创建测试物业
    property_in_order = PropertyCreate(
        name="测试物业ForOrder",
        address="测试物业地址ForOrder",
        contact_name="物业联系人ForOrder",
        contact_phone="13800001123"
    )
    db_property_order = crud_property.create_with_manager(db, obj_in=property_in_order, manager_id=db_prop_mgr_user_order.id)

    # 创建测试小区
    community_in_order = CommunityCreate(
        name="测试小区ForOrder", 
        address="测试小区地址ForOrder"
    )
    db_community_order = crud_community.create_with_property(db, obj_in=community_in_order, property_id=db_property_order.id)

    # 创建测试用户 (客户角色用于创建地址和订单)
    cust_user_order_in = UserCreate(
        username="testuser_order_cust",
        email="test_order_cust@example.com",
        phone="13800001124",
        password="testpassword",
        full_name="测试客户ForOrder",
        role=UserRole.CUSTOMER
    )
    db_cust_user_order = user.create(db, obj_in=cust_user_order_in)
    
    # 创建测试地址
    address_in_order = AddressCreate(
        address="订单测试街道地址456号",
        community_id=db_community_order.id, 
        building_number="栋2",
        room_number="房202",
        contact_name="订单地址联系人李四",
        contact_phone="13800001125",
        is_default=True
    )
    db_address_order = address.create_with_user(db, obj_in=address_in_order, user_id=db_cust_user_order.id)
    
    # 创建测试订单
    order_in = OrderCreate(
        address_id=db_address_order.id,
        waste_type="建筑垃圾-订单测试",
        waste_volume=3.5
    )
    db_order = order.create_with_customer(db, obj_in=order_in, customer_id=db_cust_user_order.id)
    
    assert db_order.address_id == db_address_order.id
    loaded_order = db.query(Order).options(joinedload(Order.address).joinedload(Address.community)).filter(Order.id == db_order.id).one()
    assert loaded_order.address is not None
    assert loaded_order.address.community is not None
    assert loaded_order.address.community.name == "测试小区ForOrder"
    assert loaded_order.waste_type == "建筑垃圾-订单测试"
    assert loaded_order.status == OrderStatus.PENDING

# 测试运输CRUD操作
def test_create_transport(db: Session):
    transport_in = TransportCreate(
        driver_name="测试司机",
        driver_phone="13800002222",
        driver_license="123456789",
        vehicle_plate="京A12345",
        vehicle_capacity=10.0,
        vehicle_volume=20.0
    )
    db_transport = transport.create(db, obj_in=transport_in)
    assert db_transport.driver_name == "测试司机"
    assert db_transport.vehicle_plate == "京A12345"
    assert db_transport.driver_status == DriverStatus.AVAILABLE

# 测试回收站CRUD操作
def test_create_recycling(db: Session):
    recycling_in = RecyclingCreate(
        name="测试回收站",
        address="测试地址",
        contact_name="测试联系人",
        contact_phone="13800003333",
        capacity=100.0
    )
    db_recycling = recycling.create(db, obj_in=recycling_in)
    assert db_recycling.name == "测试回收站"
    assert db_recycling.capacity == 100.0
    assert db_recycling.status == RecyclingStatus.ACTIVE

# 测试物业CRUD操作
def test_create_property(db: Session):
    # 创建测试用户
    user_in = UserCreate(
        username="testproperty_crud",
        email="testproperty_crud@example.com",
        phone="13800001118",
        password="testpassword",
        full_name="测试物业用户CRUD",
        role=UserRole.PROPERTY
    )
    db_user = user.create(db, obj_in=user_in)
    
    # 创建测试物业
    property_in = PropertyCreate(
        name="测试物业CRUD",
        address="测试地址CRUD",
        contact_name="测试联系人CRUD",
        contact_phone="13800001119"
    )
    db_property = crud_property.create_with_manager(db, obj_in=property_in, manager_id=db_user.id)
    assert db_property.name == "测试物业CRUD"
    assert len(db_property.property_managers) == 1
    pm_entry = db.query(PropertyManager).filter(PropertyManager.property_id == db_property.id, PropertyManager.manager_id == db_user.id).first()
    assert pm_entry is not None
    assert pm_entry.manager_id == db_user.id
    assert pm_entry.is_primary == True
    assert pm_entry.community_id is None
    
    # 创建社区
    community_in = CommunityCreate(
        name="测试小区CRUD",
        address="测试小区地址CRUD"
    )
    db_community = crud_community.create_with_property(db, obj_in=community_in, property_id=db_property.id)
    assert db_community.name == "测试小区CRUD"
    assert db_community.property_id == db_property.id

# 测试添加物业管理员
def test_add_property_manager(db: Session):
    # 创建主要管理员用户
    primary_manager_user_in = UserCreate(
        username="primarymanager_crud_add",
        email="primary_crud_add@example.com",
        phone="13800001120",
        password="testpassword",
        full_name="主要管理员CRUD_ADD",
        role=UserRole.PROPERTY
    )
    db_primary_manager = user.create(db, obj_in=primary_manager_user_in)
    
    property_in = PropertyCreate(
        name="测试物业_CRUD_ADD_PM",
        address="测试地址_CRUD_ADD_PM",
        contact_name="测试联系人",
        contact_phone="13800001121"
    )
    db_property = crud_property.create_with_manager(db, obj_in=property_in, manager_id=db_primary_manager.id)
    
    # 创建社区
    community_in_obj = CommunityCreate(
        name="测试小区_CRUD_ADD_PM",
        address="测试小区地址_CRUD_ADD_PM"
    )
    db_community = crud_community.create_with_property(db, obj_in=community_in_obj, property_id=db_property.id)
    
    # 创建新的普通管理员用户
    new_manager_user_in = UserCreate(
        username="newmanager_crud_add",
        email="new_crud_add@example.com",
        phone="13800002223",
        password="testpassword",
        full_name="新管理员CRUD_ADD",
        role=UserRole.PROPERTY
    )
    db_new_manager = user.create(db, obj_in=new_manager_user_in)
    
    # 添加新管理员
    manager_create_schema = PropertyManagerCreate(
        manager_id=db_new_manager.id,
        role="普通管理员",
        is_primary=False,
        community_id=db_community.id
    )
    db_added_manager = crud_prop_manager.create(db, obj_in=manager_create_schema, property_id=db_property.id)
    
    assert db_added_manager.manager_id == db_new_manager.id
    assert db_added_manager.role == "普通管理员"
    assert not db_added_manager.is_primary
    assert db_added_manager.community_id == db_community.id
    
    # Verify count
    managers_count = db.query(PropertyManager).filter(PropertyManager.property_id == db_property.id).count()
    assert managers_count == 2

# 测试更新物业管理员
def test_update_property_manager(db: Session):
    primary_manager_user_in = UserCreate(
        username="primarymanager_crud_upd", email="primary_crud_upd@example.com", phone="13800001122",
        password="testpassword", full_name="主要管理员CRUD_UPD", role=UserRole.PROPERTY)
    db_primary_manager = user.create(db, obj_in=primary_manager_user_in)
    
    property_in = PropertyCreate(
        name="测试物业_CRUD_UPD_PM", address="测试地址_CRUD_UPD_PM",
        contact_name="测试联系人", contact_phone="13800001123")
    db_property = crud_property.create_with_manager(db, obj_in=property_in, manager_id=db_primary_manager.id)
    
    community1_in = CommunityCreate(name="小区1_CRUD_UPD", address="地址1")
    db_community1 = crud_community.create_with_property(db, obj_in=community1_in, property_id=db_property.id)
    community2_in = CommunityCreate(name="小区2_CRUD_UPD", address="地址2")
    db_community2 = crud_community.create_with_property(db, obj_in=community2_in, property_id=db_property.id)

    new_manager_user_in = UserCreate(
        username="newmanager_crud_upd", email="new_crud_upd@example.com", phone="13800002224",
        password="testpassword", full_name="新管理员CRUD_UPD", role=UserRole.PROPERTY)
    db_new_manager = user.create(db, obj_in=new_manager_user_in)
    
    manager_create_schema = PropertyManagerCreate(
        manager_id=db_new_manager.id, role="普通管理员", is_primary=False, community_id=db_community1.id)
    db_manager_to_update = crud_prop_manager.create(db, obj_in=manager_create_schema, property_id=db_property.id)
    
    update_schema = PropertyManagerUpdate(role="高级管理员", community_id=db_community2.id)
    
    updated_manager = crud_prop_manager.update(db, db_obj=db_manager_to_update, obj_in=update_schema)
    assert updated_manager.role == "高级管理员"
    assert not updated_manager.is_primary
    assert updated_manager.community_id == db_community2.id

    # Test promoting to primary (and ensuring community_id becomes None)
    update_to_primary_schema = PropertyManagerUpdate(is_primary=True)
    # First, demote the original primary manager to allow promotion of another one
    original_primary_pm = db.query(PropertyManager).filter(PropertyManager.property_id == db_property.id, PropertyManager.is_primary == True).first()
    assert original_primary_pm is not None
    crud_prop_manager.update(db, db_obj=original_primary_pm, obj_in=PropertyManagerUpdate(is_primary=False, community_id=db_community1.id))

    promoted_manager = crud_prop_manager.update(db, db_obj=db_manager_to_update, obj_in=update_to_primary_schema)
    assert promoted_manager.is_primary is True
    assert promoted_manager.community_id is None

# 测试移除物业管理员
def test_remove_property_manager(db: Session):
    primary_manager_user_in = UserCreate(
        username="primarymanager_crud_rem", email="primary_crud_rem@example.com", phone="13800001124",
        password="testpassword", full_name="主要管理员CRUD_REM", role=UserRole.PROPERTY)
    db_primary_manager = user.create(db, obj_in=primary_manager_user_in)
    
    property_in = PropertyCreate(
        name="测试物业_CRUD_REM_PM", address="测试地址_CRUD_REM_PM",
        contact_name="测试联系人", contact_phone="13800001125")
    db_property = crud_property.create_with_manager(db, obj_in=property_in, manager_id=db_primary_manager.id)
    
    community_in_obj = CommunityCreate(name="测试小区_CRUD_REM_PM", address="测试小区地址_CRUD_REM_PM")
    db_community = crud_community.create_with_property(db, obj_in=community_in_obj, property_id=db_property.id)
    
    new_manager_user_in = UserCreate(
        username="newmanager_crud_rem", email="new_crud_rem@example.com", phone="13800002225",
        password="testpassword", full_name="新管理员CRUD_REM", role=UserRole.PROPERTY)
    db_new_manager = user.create(db, obj_in=new_manager_user_in)
    
    manager_create_schema = PropertyManagerCreate(
        manager_id=db_new_manager.id, role="待移除管理员", is_primary=False, community_id=db_community.id)
    db_manager_to_remove = crud_prop_manager.create(db, obj_in=manager_create_schema, property_id=db_property.id)
    
    initial_pm_count = db.query(PropertyManager).filter(PropertyManager.property_id == db_property.id).count()
    assert initial_pm_count == 2

    removed_manager = crud_prop_manager.remove(db, id=db_manager_to_remove.id)
    assert removed_manager.id == db_manager_to_remove.id
    
    final_pm_count = db.query(PropertyManager).filter(PropertyManager.property_id == db_property.id).count()
    assert final_pm_count == initial_pm_count - 1
    
    # Ensure the correct one was removed
    remaining_manager = db.query(PropertyManager).filter(PropertyManager.property_id == db_property.id).first()
    assert remaining_manager is not None
    assert remaining_manager.manager_id == db_primary_manager.id
    assert remaining_manager.is_primary is True

def test_get_orders_by_property_manager(db: Session):
    # 1. Create Property
    prop_owner_user = user.create(db, obj_in=UserCreate(username="prop_owner_get_orders", email="po_get@example.com", phone="13800003001", password="pw", role=UserRole.PROPERTY, full_name="Prop Owner GetOrders"))
    test_property = crud_property.create_with_manager(db, obj_in=PropertyCreate(name="Test Property for GetOrders", address="Property Address", contact_name="Prop Contact", contact_phone="13800003002"), manager_id=prop_owner_user.id)
    
    # 2. Create Communities for this Property
    community_A = crud_community.create_with_property(db, obj_in=CommunityCreate(name="Community A for GetOrders", address="Comm A Addr"), property_id=test_property.id)
    community_B = crud_community.create_with_property(db, obj_in=CommunityCreate(name="Community B for GetOrders", address="Comm B Addr"), property_id=test_property.id)

    # 3. Create Property Managers
    # Primary Manager (already created as prop_owner_user when creating property, now ensure they are primary)
    # The create_with_manager in crud_property already makes this user a primary manager.
    primary_manager_pm_record = db.query(PropertyManager).filter(PropertyManager.property_id == test_property.id, PropertyManager.manager_id == prop_owner_user.id).first()
    assert primary_manager_pm_record is not None
    assert primary_manager_pm_record.is_primary == True

    # Normal Manager A (for Community A)
    normal_manager_user_A = user.create(db, obj_in=UserCreate(username="norm_mgr_A_get_orders", email="nma_get@example.com", phone="13800003003", password="pw", role=UserRole.PROPERTY, full_name="Normal Mgr A"))
    crud_prop_manager.create(db, obj_in=PropertyManagerCreate(manager_id=normal_manager_user_A.id, role="Normal Manager A", is_primary=False, community_id=community_A.id), property_id=test_property.id)

    # Normal Manager B (for Community B)
    normal_manager_user_B = user.create(db, obj_in=UserCreate(username="norm_mgr_B_get_orders", email="nmb_get@example.com", phone="13800003004", password="pw", role=UserRole.PROPERTY, full_name="Normal Mgr B"))
    crud_prop_manager.create(db, obj_in=PropertyManagerCreate(manager_id=normal_manager_user_B.id, role="Normal Manager B", is_primary=False, community_id=community_B.id), property_id=test_property.id)

    # Unrelated Manager (not associated with test_property or its communities directly in a way that grants order access according to new logic)
    unrelated_manager_user = user.create(db, obj_in=UserCreate(username="unrel_mgr_get_orders", email="unrel_get@example.com", phone="13800003005", password="pw", role=UserRole.PROPERTY, full_name="Unrelated Mgr"))
    # This manager might be associated with another property or no specific community of test_property

    # 4. Create Customer and Addresses/Orders
    customer_user = user.create(db, obj_in=UserCreate(username="cust_get_orders", email="cust_get@example.com", phone="13800003006", password="pw", role=UserRole.CUSTOMER, full_name="Customer GetOrders"))
    
    address_A1 = address.create_with_user(db, obj_in=AddressCreate(address="Addr A1", community_id=community_A.id, building_number="A1", room_number="101", contact_name="CA1", contact_phone="13800003007"), user_id=customer_user.id)
    order_A1 = order.create_with_customer(db, obj_in=OrderCreate(address_id=address_A1.id, waste_type="Type A1", waste_volume=1.0), customer_id=customer_user.id)

    address_A2 = address.create_with_user(db, obj_in=AddressCreate(address="Addr A2", community_id=community_A.id, building_number="A2", room_number="102", contact_name="CA2", contact_phone="13800003008"), user_id=customer_user.id)
    order_A2 = order.create_with_customer(db, obj_in=OrderCreate(address_id=address_A2.id, waste_type="Type A2", waste_volume=1.0), customer_id=customer_user.id)

    address_B1 = address.create_with_user(db, obj_in=AddressCreate(address="Addr B1", community_id=community_B.id, building_number="B1", room_number="101", contact_name="CB1", contact_phone="13800003009"), user_id=customer_user.id)
    order_B1 = order.create_with_customer(db, obj_in=OrderCreate(address_id=address_B1.id, waste_type="Type B1", waste_volume=1.0), customer_id=customer_user.id)

    # 5. Test get_by_property_manager
    # Primary Manager (prop_owner_user)
    orders_for_primary = order.get_by_property_manager(db, manager_user_id=prop_owner_user.id)
    order_ids_for_primary = {o.id for o in orders_for_primary}
    assert {order_A1.id, order_A2.id, order_B1.id} == order_ids_for_primary
    assert len(orders_for_primary) == 3

    # Normal Manager A
    orders_for_normal_A = order.get_by_property_manager(db, manager_user_id=normal_manager_user_A.id)
    order_ids_for_normal_A = {o.id for o in orders_for_normal_A}
    assert {order_A1.id, order_A2.id} == order_ids_for_normal_A
    assert len(orders_for_normal_A) == 2

    # Normal Manager B
    orders_for_normal_B = order.get_by_property_manager(db, manager_user_id=normal_manager_user_B.id)
    order_ids_for_normal_B = {o.id for o in orders_for_normal_B}
    assert {order_B1.id} == order_ids_for_normal_B
    assert len(orders_for_normal_B) == 1

    # Unrelated Manager
    orders_for_unrelated = order.get_by_property_manager(db, manager_user_id=unrelated_manager_user.id)
    assert len(orders_for_unrelated) == 0