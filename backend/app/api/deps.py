from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import DEFAULT_ALGORITHM
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.crud.crud_user import user
from app.schemas.user import TokenPayload, UserInDB

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

def get_db() -> Generator:
    """获取数据库会话"""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)) -> User:
    """获取当前用户"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[DEFAULT_ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无法验证凭证",
        )
    
    user_id = token_data.sub
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    user_obj = user.get(db, id=user_id)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return user_obj

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前激活用户"""
    if not user.is_active(current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户未激活"
        )
    return current_user

def get_current_active_superuser(current_user: User = Depends(get_current_active_user)) -> User:
    """获取当前超级管理员用户"""
    if not user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    return current_user

def get_current_property_user(current_user: User = Depends(get_current_active_user)) -> User:
    """获取当前物业用户"""
    if current_user.role != UserRole.PROPERTY and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要物业管理员权限"
        )
    return current_user

def get_current_transport_user(current_user: User = Depends(get_current_active_user)) -> User:
    """获取当前运输用户"""
    if current_user.role != UserRole.TRANSPORT and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要运输管理员权限"
        )
    return current_user

def get_current_recycling_user(current_user: User = Depends(get_current_active_user)) -> User:
    """获取当前回收处置用户"""
    if current_user.role != UserRole.RECYCLING and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要回收处置管理员权限"
        )
    return current_user