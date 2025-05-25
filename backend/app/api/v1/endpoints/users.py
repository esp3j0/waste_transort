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
    UserUpdateMe
)

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def read_user_me(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取当前用户信息"""
    return UserResponse.model_validate(current_user).model_dump()

@router.put("/me", response_model=UserResponse)
async def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdateMe,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """更新当前用户信息"""
    update_data = user_in.model_dump(exclude_unset=True)
    
    update_data.pop("role", None)
    update_data.pop("is_superuser", None)
    update_data.pop("is_active", None)
    update_data.pop("username", None)

    user_obj = user.update(db, db_obj=current_user, obj_in=update_data)
    return UserResponse.model_validate(user_obj).model_dump()

@router.get("/", response_model=List[UserResponse])
async def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_superuser)
) -> Any:
    """获取所有用户列表（仅限超级管理员）"""
    users_db = user.get_multi(db, skip=skip, limit=limit)
    return [UserResponse.model_validate(u).model_dump() for u in users_db]

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user: User = Depends(get_current_active_superuser)
) -> Any:
    """创建新用户（仅限超级管理员）"""
    user_by_username = user.get_by_username(db, username=user_in.username)
    if user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    if hasattr(user_in, 'phone') and user_in.phone:
        user_by_phone = user.get_by_phone(db, phone=user_in.phone)
        if user_by_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已被注册"
            )
    
    if hasattr(user_in, 'email') and user_in.email:
        user_by_email = user.get_by_email(db, email=user_in.email)
        if user_by_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
    
    user_obj = user.create(db, obj_in=user_in)
    return UserResponse.model_validate(user_obj).model_dump()

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
    return UserResponse.model_validate(user_obj).model_dump()

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
    
    updated_user_obj = user.update(db, db_obj=user_obj, obj_in=user_in)
    return UserResponse.model_validate(updated_user_obj).model_dump()

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: User = Depends(get_current_active_superuser)
) -> None:
    """删除指定用户（仅限超级管理员）"""
    user_obj = user.get(db, id=user_id)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    if user_obj.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="超级管理员不能删除自己。"
        )
    user.remove(db, id=user_id)
    return