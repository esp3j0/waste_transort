import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from app.crud.crud_user import user
from app.schemas.user import UserCreate
from app.models.user import UserRole

# 测试登录API
def test_login(client: TestClient, db: Session):
    # 创建测试用户
    user_in = UserCreate(
        username="testlogin",
        email="testlogin@example.com",
        phone="13800001111",
        password="testpassword",
        full_name="测试登录用户",
        role=UserRole.CUSTOMER
    )
    db_user = user.create(db, obj_in=user_in)
    
    # 测试登录
    login_data = {
        "username": "testlogin",
        "password": "testpassword"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

# 测试登录失败
def test_login_wrong_password(client: TestClient, db: Session):
    # 创建测试用户
    user_in = UserCreate(
        username="testwrongpw",
        email="testwrongpw@example.com",
        phone="13800002222",
        password="testpassword",
        full_name="测试登录失败用户",
        role=UserRole.CUSTOMER
    )
    db_user = user.create(db, obj_in=user_in)
    
    # 测试错误密码登录
    login_data = {
        "username": "testwrongpw",
        "password": "wrongpassword"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401

# 测试注册API
def test_register(client: TestClient, db: Session):
    # 测试注册新用户
    register_data = {
        "username": "testregister",
        "email": "testregister@example.com",
        "phone": "13800003333",
        "password": "testpassword",
        "full_name": "测试注册用户",
        "role": UserRole.CUSTOMER
    }
    response = client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

# 测试重复注册
def test_register_duplicate(client: TestClient, db: Session):
    # 创建测试用户
    user_in = UserCreate(
        username="testduplicate",
        email="testduplicate@example.com",
        phone="13800004444",
        password="testpassword",
        full_name="测试重复注册用户",
        role=UserRole.CUSTOMER
    )
    db_user = user.create(db, obj_in=user_in)
    
    # 测试重复注册
    register_data = {
        "username": "testduplicate",
        "email": "another@example.com",
        "phone": "13800005555",
        "password": "testpassword",
        "full_name": "测试重复注册用户2",
        "role": UserRole.CUSTOMER
    }
    response = client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 400

# 测试微信登录API
def test_wx_login(client: TestClient, db: Session):
    # 由于微信登录需要真实的code，这里只测试接口是否可访问
    response = client.post("/api/v1/auth/wx-login?code=test_code")
    # 目前只是示例实现，应该返回200
    assert response.status_code == 200
    assert "access_token" in response.json()