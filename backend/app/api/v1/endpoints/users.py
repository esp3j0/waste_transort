from typing import Any, List
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_active_user,
    get_current_active_superuser,
    get_db
)
from app.core.config import settings
from app.core.security import create_access_token
from app.crud.crud_user import user
from app.models.user import User, UserRole
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    Token
)

router = APIRouter()

@router.post("/login/access-token", response_model=Token)
async def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """获取OAuth2兼容的令牌"""
    user_obj = user.authenticate(
        db, username=form_data.username, password=form_data.password
    )
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    if not user.is_active(user_obj):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户未激活"
        )
    
    access_token = create_access_token(subject=user_obj.id)
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate
) -> Any:
    """注册新用户"""
    # 检查用户名是否已存在
    user_by_username = user.get_by_username(db, username=user_in.username)
    if user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查手机号是否已存在
    if user_in.phone:
        user_by_phone = user.get_by_phone(db, phone=user_in.phone)
        if user_by_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已被注册"
            )
    
    # 检查邮箱是否已存在
    if user_in.email:
        user_by_email = user.get_by_email(db, email=user_in.email)
        if user_by_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
    
    # 默认注册为普通用户，管理员和其他角色需要超级管理员创建
    if user_in.role not in [UserRole.CUSTOMER]:
        user_in.role = UserRole.CUSTOMER
    
    user_obj = user.create(db, obj_in=user_in)
    return user_obj

@router.get("/me", response_model=UserResponse)
async def read_user_me(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取当前用户信息"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """更新当前用户信息"""
    # 不允许普通用户修改自己的角色和超级管理员状态
    if user_in.role is not None or user_in.is_superuser is not False:
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="普通用户不能修改角色和管理员状态"
            )
    
    user_obj = user.update(db, db_obj=current_user, obj_in=user_in)
    return user_obj

@router.get("/", response_model=List[UserResponse])
async def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_superuser)
) -> Any:
    """获取所有用户列表（仅限超级管理员）"""
    users = user.get_multi(db, skip=skip, limit=limit)
    return users

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user: User = Depends(get_current_active_superuser)
) -> Any:
    """创建新用户（仅限超级管理员）"""
    # 检查用户名是否已存在
    user_by_username = user.get_by_username(db, username=user_in.username)
    if user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查手机号是否已存在
    if user_in.phone:
        user_by_phone = user.get_by_phone(db, phone=user_in.phone)
        if user_by_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已被注册"
            )
    
    # 检查邮箱是否已存在
    if user_in.email:
        user_by_email = user.get_by_email(db, email=user_in.email)
        if user_by_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
    
    user_obj = user.create(db, obj_in=user_in)
    return user_obj

@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: User = Depends(get_current_active_superuser)
) -> Any:
    """获取指定用户信息（仅限超级管理员）"""
    user_obj = user.get(db, id=user_id)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user_obj

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_superuser)
) -> Any:
    """更新指定用户信息（仅限超级管理员）"""
    user_obj = user.get(db, id=user_id)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    user_obj = user.update(db, db_obj=user_obj, obj_in=user_in)
    return user_obj

@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: User = Depends(get_current_active_superuser)
) -> Any:
    """删除指定用户（仅限超级管理员）"""
    user_obj = user.get(db, id=user_id)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不允许删除自己
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除当前登录的用户"
        )
    
    user_obj = user.remove(db, id=user_id)
    return user_obj