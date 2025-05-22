from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, validator
from app.models.user import UserRole

# 共享属性基类
class UserBase(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    wx_openid: Optional[str] = None

# 创建用户时需要的属性
class UserCreate(UserBase):
    username: str
    phone: str
    password: str
    role: str = UserRole.CUSTOMER
    
    @validator('role')
    def validate_role(cls, v):
        if v not in [role.value for role in UserRole]:
            raise ValueError(f'角色必须是以下之一: {[role.value for role in UserRole]}')
        return v

# 更新用户时可以更新的属性
class UserUpdate(UserBase):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

# API响应中的用户信息
class UserResponse(UserBase):
    id: int
    
    class Config:
        orm_mode = True

# 存储在令牌中的用户信息
class UserInDB(UserResponse):
    hashed_password: str

# 令牌相关模型
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None
    exp: Optional[int] = None