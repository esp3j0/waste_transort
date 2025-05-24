import pytest
from sqlalchemy.orm import Session

from app.crud import user, property, order, transport, recycling, address, community
from app.models.user import User, UserRole
from app.models.order import Order, OrderStatus
from app.models.transport import Transport, DriverStatus
from app.models.recycling import Recycling, RecyclingStatus
from app.schemas.user import UserCreate
from app.schemas.order import OrderCreate
from app.schemas.transport import TransportCreate
from app.schemas.recycling import RecyclingCreate
from app.schemas.address import AddressCreate
from app.schemas.property import PropertyCreate
from app.schemas.property_manager import PropertyManagerCreate, PropertyManagerUpdate
from app.schemas.community import CommunityCreate

# 测试用户CRUD操作
def test_create_user(db: Session):
    user_in = UserCreate(
        username="testuser",
        email="test@example.com",
        phone="13800001111",
        password="testpassword",
        full_name="测试用户",
        role=UserRole.CUSTOMER
    )
    db_user = user.create(db, obj_in=user_in)
    assert db_user.username == "testuser"
    assert db_user.email == "test@example.com"
    assert db_user.role == UserRole.CUSTOMER

# 测试地址CRUD操作
def test_create_address(db: Session):
    # 创建测试用户
    user_in = UserCreate(
        username="testuser",
        email="test@example.com",
        phone="13800001111",
        password="testpassword",
        full_name="测试用户",
        role=UserRole.CUSTOMER
    )
    db_user = user.create(db, obj_in=user_in)
    
    # 创建测试地址
    address_in = AddressCreate(
        address="测试地址",
        community_name="测试小区",
        building_number="1",
        room_number="101",
        contact_name="测试联系人",
        contact_phone="13800001111",
        is_default=True
    )
    db_address = address.create_with_user(db, obj_in=address_in, user_id=db_user.id)
    assert db_address.community_name == "测试小区"
    assert db_address.is_default == True

# 测试订单CRUD操作
def test_create_order(db: Session):
    # 创建测试用户
    user_in = UserCreate(
        username="testuser",
        email="test@example.com",
        phone="13800001111",
        password="testpassword",
        full_name="测试用户",
        role=UserRole.CUSTOMER
    )
    db_user = user.create(db, obj_in=user_in)
    
    # 创建测试地址
    address_in = AddressCreate(
        address="测试地址",
        community_name="测试小区",
        building_number="1",
        room_number="101",
        contact_name="测试联系人",
        contact_phone="13800001111",
        is_default=True
    )
    db_address = address.create_with_user(db, obj_in=address_in, user_id=db_user.id)
    
    # 创建测试订单
    order_in = OrderCreate(
        address_id=db_address.id,
        waste_type="建筑垃圾",
        waste_volume=2.5
    )
    db_order = order.create_with_customer(db, obj_in=order_in, customer_id=db_user.id)
    assert db_order.address.community_name == "测试小区"
    assert db_order.waste_type == "建筑垃圾"
    assert db_order.status == OrderStatus.PENDING

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
        username="testproperty",
        email="testproperty@example.com",
        phone="13800001111",
        password="testpassword",
        full_name="测试物业用户",
        role=UserRole.PROPERTY
    )
    db_user = user.create(db, obj_in=user_in)
    
    # 创建测试物业
    property_in = PropertyCreate(
        name="测试物业",
        address="测试地址",
        contact_name="测试联系人",
        contact_phone="13800001111"
    )
    db_property = property.create_with_manager(db, obj_in=property_in, manager_id=db_user.id)
    assert db_property.name == "测试物业"
    assert len(db_property.property_managers) == 1
    assert db_property.property_managers[0].manager_id == db_user.id
    assert db_property.property_managers[0].is_primary == True
    
    # 创建社区
    community_in = CommunityCreate(
        name="测试小区",
        address="测试小区地址"
    )
    db_community = community.create_with_property(db, obj_in=community_in, property_id=db_property.id)
    assert db_community.name == "测试小区"
    assert db_community.property_id == db_property.id

# 测试添加物业管理员
def test_add_property_manager(db: Session):
    # 创建主要管理员和物业
    primary_manager_in = UserCreate(
        username="primarymanager",
        email="primary@example.com",
        phone="13800001111",
        password="testpassword",
        full_name="主要管理员",
        role=UserRole.PROPERTY
    )
    db_primary_manager = user.create(db, obj_in=primary_manager_in)
    
    property_in = PropertyCreate(
        name="测试物业",
        address="测试地址",
        contact_name="测试联系人",
        contact_phone="13800001111"
    )
    db_property = property.create_with_manager(db, obj_in=property_in, manager_id=db_primary_manager.id)
    
    # 创建社区
    community_in = CommunityCreate(
        name="测试小区",
        address="测试小区地址"
    )
    community.create_with_property(db, obj_in=community_in, property_id=db_property.id)
    
    # 创建新的管理员用户
    new_manager_in = UserCreate(
        username="newmanager",
        email="new@example.com",
        phone="13800002222",
        password="testpassword",
        full_name="新管理员",
        role=UserRole.PROPERTY
    )
    db_new_manager = user.create(db, obj_in=new_manager_in)
    
    # 添加新管理员
    manager_data = PropertyManagerCreate(
        manager_id=db_new_manager.id,
        role="普通管理员",
        is_primary=False
    )
    db_manager = property.add_manager(db, property_id=db_property.id, obj_in=manager_data)
    assert db_manager.manager_id == db_new_manager.id
    assert db_manager.role == "普通管理员"
    assert not db_manager.is_primary
    assert len(db_property.property_managers) == 2

# 测试更新物业管理员
def test_update_property_manager(db: Session):
    # 创建主要管理员和物业
    primary_manager_in = UserCreate(
        username="primarymanager",
        email="primary@example.com",
        phone="13800001111",
        password="testpassword",
        full_name="主要管理员",
        role=UserRole.PROPERTY
    )
    db_primary_manager = user.create(db, obj_in=primary_manager_in)
    
    property_in = PropertyCreate(
        name="测试物业",
        address="测试地址",
        contact_name="测试联系人",
        contact_phone="13800001111"
    )
    db_property = property.create_with_manager(db, obj_in=property_in, manager_id=db_primary_manager.id)
    
    # 创建社区
    community_in = CommunityCreate(
        name="测试小区",
        address="测试小区地址"
    )
    community.create_with_property(db, obj_in=community_in, property_id=db_property.id)
    
    # 创建新的管理员用户
    new_manager_in = UserCreate(
        username="newmanager",
        email="new@example.com",
        phone="13800002222",
        password="testpassword",
        full_name="新管理员",
        role=UserRole.PROPERTY
    )
    db_new_manager = user.create(db, obj_in=new_manager_in)
    
    # 添加新管理员
    manager_data = PropertyManagerCreate(
        manager_id=db_new_manager.id,
        role="普通管理员",
        is_primary=False
    )
    db_manager = property.add_manager(db, property_id=db_property.id, obj_in=manager_data)
    
    # 更新管理员信息
    update_data = PropertyManagerUpdate(
        role="高级管理员",
        is_primary=False
    )
    updated_manager = property.update_manager(db, manager_id=db_manager.id, obj_in=update_data)
    assert updated_manager.role == "高级管理员"
    assert not updated_manager.is_primary

# 测试移除物业管理员
def test_remove_property_manager(db: Session):
    # 创建主要管理员和物业
    primary_manager_in = UserCreate(
        username="primarymanager",
        email="primary@example.com",
        phone="13800001111",
        password="testpassword",
        full_name="主要管理员",
        role=UserRole.PROPERTY
    )
    db_primary_manager = user.create(db, obj_in=primary_manager_in)
    
    property_in = PropertyCreate(
        name="测试物业",
        address="测试地址",
        contact_name="测试联系人",
        contact_phone="13800001111"
    )
    db_property = property.create_with_manager(db, obj_in=property_in, manager_id=db_primary_manager.id)
    
    # 创建社区
    community_in = CommunityCreate(
        name="测试小区",
        address="测试小区地址"
    )
    community.create_with_property(db, obj_in=community_in, property_id=db_property.id)
    
    # 创建新的管理员用户
    new_manager_in = UserCreate(
        username="newmanager",
        email="new@example.com",
        phone="13800002222",
        password="testpassword",
        full_name="新管理员",
        role=UserRole.PROPERTY
    )
    db_new_manager = user.create(db, obj_in=new_manager_in)
    
    # 添加新管理员
    manager_data = PropertyManagerCreate(
        manager_id=db_new_manager.id,
        role="普通管理员",
        is_primary=False
    )
    db_manager = property.add_manager(db, property_id=db_property.id, obj_in=manager_data)
    
    # 移除管理员
    property.remove_manager(db, manager_id=db_manager.id)
    assert len(db_property.property_managers) == 1
    assert db_property.property_managers[0].manager_id == db_primary_manager.id