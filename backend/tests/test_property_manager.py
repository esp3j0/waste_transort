import pytest
import random
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.crud import user, property, community
from app.schemas.user import UserCreate
from app.schemas.property import PropertyCreate, PropertyUpdate, PropertyResponse
from app.schemas.property_manager import PropertyManagerCreate, PropertyManagerUpdate, PropertyManagerResponse
from app.schemas.community import CommunityCreate
from app.models.user import UserRole
from app.core.security import create_access_token

# 辅助函数：创建不同角色的测试用户并返回token
def create_user_with_role(db: Session, role, is_superuser=False,username_suffix="_primary"):
    random_number = random.randint(1000, 9999)
    username = f"test{role.lower()}_{random_number}{username_suffix}"
    
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

# 辅助函数：创建测试物业和社区
def create_test_property(db: Session, manager_id: int):
    # 创建物业
    property_in = PropertyCreate(
        name="测试物业",
        address="测试地址",
        contact_name="测试联系人",
        contact_phone="13800001111"
    )
    db_property = property.create_with_manager(db, obj_in=property_in, manager_id=manager_id)
    
    # 创建社区
    community_in = CommunityCreate(
        name="测试小区",
        address="测试小区地址"
    )
    db_community = community.create_with_property(db, obj_in=community_in, property_id=db_property.id)
    
    return db_property

# 测试添加物业管理员
def test_add_property_manager(client: TestClient, db: Session):
    # 创建主要管理员和物业
    primary_manager, primary_token = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_primary")
    test_property = create_test_property(db, primary_manager.id)
    
    # 创建新的管理员用户
    new_manager, _ = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_new")
    
    # 测试添加管理员
    manager_data = {
        "manager_id": new_manager.id,
        "role": "普通管理员",
        "is_primary": False
    }
    headers = {"Authorization": f"Bearer {primary_token}"}
    response = client.post(
        f"/api/v1/properties/{test_property.id}/managers",
        json=manager_data,
        headers=headers
    )
    assert response.status_code == 200
    manager_data = response.json()
    assert manager_data["manager_id"] == new_manager.id
    assert manager_data["role"] == "普通管理员"
    assert not manager_data["is_primary"]

# 测试添加主要管理员（应该失败）
def test_add_primary_manager_failure(client: TestClient, db: Session):
    # 创建主要管理员和物业
    primary_manager, primary_token = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_primary")
    test_property = create_test_property(db, primary_manager.id)
    
    # 创建新的管理员用户
    new_manager, _ = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_new")
    
    # 测试添加主要管理员（应该失败）
    manager_data = {
        "manager_id": new_manager.id,
        "role": "主要管理员",
        "is_primary": True
    }
    headers = {"Authorization": f"Bearer {primary_token}"}
    response = client.post(
        f"/api/v1/properties/{test_property.id}/managers",
        json=manager_data,
        headers=headers
    )
    assert response.status_code == 400
    assert "已存在主要管理员" in response.json()["detail"]

# 测试更新物业管理员
def test_update_property_manager(client: TestClient, db: Session):
    # 创建主要管理员和物业
    primary_manager, primary_token = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_primary")
    test_property = create_test_property(db, primary_manager.id)
    
    # 创建新的管理员用户
    new_manager, _ = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_new")
    
    # 添加新管理员
    manager_data = {
        "manager_id": new_manager.id,
        "role": "普通管理员",
        "is_primary": False
    }
    headers = {"Authorization": f"Bearer {primary_token}"}
    response = client.post(
        f"/api/v1/properties/{test_property.id}/managers",
        json=manager_data,
        headers=headers
    )
    assert response.status_code == 200
    manager_id = response.json()["id"]
    
    # 测试更新管理员信息
    update_data = {
        "role": "高级管理员",
        "is_primary": False
    }
    response = client.put(
        f"/api/v1/properties/{test_property.id}/managers/{manager_id}",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 200
    updated_data = response.json()
    assert updated_data["role"] == "高级管理员"

# 测试移除物业管理员
def test_remove_property_manager(client: TestClient, db: Session):
    # 创建主要管理员和物业
    primary_manager, primary_token = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_primary")
    test_property = create_test_property(db, primary_manager.id)
    
    # 创建新的管理员用户
    new_manager, _ = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_new")
    
    # 添加新管理员
    manager_data = {
        "manager_id": new_manager.id,
        "role": "普通管理员",
        "is_primary": False
    }
    headers = {"Authorization": f"Bearer {primary_token}"}
    response = client.post(
        f"/api/v1/properties/{test_property.id}/managers",
        json=manager_data,
        headers=headers
    )
    assert response.status_code == 200
    manager_id = response.json()["id"]
    
    # 测试移除管理员
    response = client.delete(
        f"/api/v1/properties/{test_property.id}/managers/{manager_id}",
        headers=headers
    )
    assert response.status_code == 200

# 测试移除主要管理员（应该失败）
def test_remove_primary_manager_failure(client: TestClient, db: Session):
    # 创建主要管理员和物业
    primary_manager, primary_token = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_primary")
    test_property = create_test_property(db, primary_manager.id)
    
    # 获取主要管理员的关联ID
    property_obj = property.get(db, id=test_property.id)
    primary_manager_rel = next(
        rel for rel in property_obj.property_managers
        if rel.manager_id == primary_manager.id
    )
    
    # 测试移除主要管理员（应该失败）
    headers = {"Authorization": f"Bearer {primary_token}"}
    response = client.delete(
        f"/api/v1/properties/{test_property.id}/managers/{primary_manager_rel.id}",
        headers=headers
    )
    assert response.status_code == 400
    assert "不能删除主要管理员" in response.json()["detail"]

# 测试非管理员用户添加管理员（应该失败）
def test_add_manager_unauthorized(client: TestClient, db: Session):
    # 创建普通物业用户和物业
    property_user, token = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_primary")
    test_property = create_test_property(db, property_user.id)
    
    # 创建新的管理员用户
    new_manager, _ = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_new")
    
    # 主管理员测试添加管理员（应该成功）
    manager_data = {
        "manager_id": new_manager.id,
        "role": "普通管理员",
        "is_primary": False
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        f"/api/v1/properties/{test_property.id}/managers",
        json=manager_data,
        headers=headers
    )
    assert response.status_code == 200
    new_token = create_access_token(new_manager.id)
    headers = {"Authorization": f"Bearer {new_token}"}
    response = client.post(
        f"/api/v1/properties/{test_property.id}/managers",
        json=manager_data,
        headers=headers
    )
    assert response.status_code == 403

    assert "只有主要管理员可以添加其他管理员" in response.json()["detail"] 