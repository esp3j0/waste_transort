import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.crud.crud_user import user
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import UserRole
from app.core.security import create_access_token

# 辅助函数：创建测试用户并返回token
def create_test_user_and_token(db: Session, is_superuser=False):
    user_in = UserCreate(
        username="testuser",
        email="testuser@example.com",
        phone="13800001111",
        password="testpassword",
        full_name="测试用户",
        role=UserRole.CUSTOMER,
        is_superuser=is_superuser
    )
    db_user = user.create(db, obj_in=user_in)
    access_token = create_access_token(db_user.id)
    return db_user, access_token

# 测试获取当前用户信息
def test_read_user_me(client: TestClient, db: Session):
    # 创建测试用户和token
    db_user, access_token = create_test_user_and_token(db)
    
    # 测试获取当前用户信息
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["username"] == "testuser"
    assert user_data["email"] == "testuser@example.com"

# 测试更新当前用户信息
def test_update_user_me(client: TestClient, db: Session):
    # 创建测试用户和token
    db_user, access_token = create_test_user_and_token(db)
    
    # 测试更新当前用户信息
    update_data = {
        "full_name": "更新后的用户名",
        "email": "updated@example.com"
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.put("/api/v1/users/me", json=update_data, headers=headers)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["full_name"] == "更新后的用户名"
    assert user_data["email"] == "updated@example.com"

# 测试普通用户无法修改自己的角色
def test_update_user_me_role_forbidden(client: TestClient, db: Session):
    # 创建测试用户和token
    db_user, access_token = create_test_user_and_token(db)
    
    # 测试普通用户尝试修改自己的角色
    update_data = {
        "role": UserRole.PROPERTY
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.put("/api/v1/users/me", json=update_data, headers=headers)
    assert response.status_code == 400

# 测试管理员获取所有用户列表
def test_read_users(client: TestClient, db: Session):
    # 创建管理员用户和token
    db_user, access_token = create_test_user_and_token(db, is_superuser=True)
    
    # 测试获取所有用户列表
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/api/v1/users/", headers=headers)
    assert response.status_code == 200
    users_data = response.json()
    assert isinstance(users_data, list)

# 测试普通用户无法获取所有用户列表
def test_read_users_forbidden(client: TestClient, db: Session):
    # 创建普通用户和token
    db_user, access_token = create_test_user_and_token(db)
    
    # 测试普通用户尝试获取所有用户列表
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/api/v1/users/", headers=headers)
    assert response.status_code == 403

# 测试管理员创建新用户
def test_create_user(client: TestClient, db: Session):
    # 创建管理员用户和token
    db_user, access_token = create_test_user_and_token(db, is_superuser=True)
    
    # 测试创建新用户
    new_user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "phone": "13800002222",
        "password": "newpassword",
        "full_name": "新用户",
        "role": UserRole.PROPERTY
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("/api/v1/users/", json=new_user_data, headers=headers)
    assert response.status_code == 201
    user_data = response.json()
    assert user_data["username"] == "newuser"
    assert user_data["role"] == UserRole.PROPERTY

# 测试管理员获取特定用户信息
def test_read_user(client: TestClient, db: Session):
    # 创建管理员用户和token
    admin_user, admin_token = create_test_user_and_token(db, is_superuser=True)
    
    # 创建普通用户
    user_in = UserCreate(
        username="usertoread",
        email="usertoread@example.com",
        phone="13800003333",
        password="testpassword",
        full_name="待读取用户",
        role=UserRole.CUSTOMER
    )
    db_user = user.create(db, obj_in=user_in)
    
    # 测试获取特定用户信息
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get(f"/api/v1/users/{db_user.id}", headers=headers)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["username"] == "usertoread"
    assert user_data["email"] == "usertoread@example.com"

# 测试管理员更新特定用户信息
def test_update_user(client: TestClient, db: Session):
    # 创建管理员用户和token
    admin_user, admin_token = create_test_user_and_token(db, is_superuser=True)
    
    # 创建普通用户
    user_in = UserCreate(
        username="usertoupdate",
        email="usertoupdate@example.com",
        phone="13800004444",
        password="testpassword",
        full_name="待更新用户",
        role=UserRole.CUSTOMER
    )
    db_user = user.create(db, obj_in=user_in)
    
    # 测试更新特定用户信息
    update_data = {
        "full_name": "已更新用户",
        "role": UserRole.PROPERTY
    }
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.put(f"/api/v1/users/{db_user.id}", json=update_data, headers=headers)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["full_name"] == "已更新用户"
    assert user_data["role"] == UserRole.PROPERTY