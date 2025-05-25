from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, validator, Field
from app.models.user import UserRole

# 共享属性基类
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    # username, role, is_active, is_superuser, wx_openid removed from here as they are not common to all create/update scenarios

# Schema for user self-registration (open endpoint)
class UserCreateOpen(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    email: Optional[EmailStr] = None # Made optional for registration, can be added later
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = None # Made optional for registration

# Schema for admin to create a user
class UserCreate(UserBase):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.CUSTOMER # Default role, admin can override
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    wx_openid: Optional[str] = None
    # email, full_name, phone inherited from UserBase and are optional
    
    @validator('role', pre=True, always=True)
    def validate_role_is_enum(cls, v):
        if isinstance(v, str):
            return UserRole(v) # Convert string to UserRole enum
        if not isinstance(v, UserRole):
            raise ValueError(f'角色必须是 UserRole 枚举类型')
        return v

# Schema for user to update their own info
class UserUpdateMe(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None 
    phone: Optional[str] = None
    # password: Optional[str] = None # Password update should be a separate endpoint/flow

# Schema for admin to update a user
class UserUpdate(UserBase):
    password: Optional[str] = Field(None, min_length=6) # Admin can change password
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    wx_openid: Optional[str] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50) # Admin can change username
    # email, full_name, phone inherited from UserBase and are optional

    @validator('role', pre=True, always=True)
    def validate_role_is_enum_optional(cls, v):
        if v is None: return v
        if isinstance(v, str):
            return UserRole(v)
        if not isinstance(v, UserRole):
            raise ValueError(f'角色必须是 UserRole 枚举类型')
        return v

# API响应中的用户信息
class UserResponse(UserBase):
    id: int
    username: str # username is always present in response
    role: UserRole
    is_active: bool
    is_superuser: bool
    wx_openid: Optional[str] = None
    
    model_config = {
        "from_attributes": True,
        "use_enum_values": True # Ensures enum values are returned as strings if needed by client
    }

# 存储在令牌中的用户信息 (not directly used by API responses, but good for internal representation)
class UserInDBBase(UserBase):
    id: int
    username: str
    hashed_password: str
    role: UserRole
    is_active: bool
    is_superuser: bool
    wx_openid: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

# 令牌相关模型
class Token(BaseModel):
    access_token: str
    token_type: str
    user: Optional[UserResponse] = None # Optionally include user info in token response

class TokenPayload(BaseModel):
    sub: Optional[int] = None
    exp: Optional[int] = None