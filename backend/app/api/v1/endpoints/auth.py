from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token
from app.core.wx_auth import get_wx_session
from app.db.session import get_db
from app.schemas.token import Token
from app.schemas.user import UserCreate
from app.schemas.auth import WxLoginRequest
from app.crud.crud_user import user as crud_user

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """
    获取OAuth2兼容的令牌，用于用户登录
    """
    user = crud_user.authenticate(db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/register", response_model=Token)
async def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    注册新用户并返回访问令牌
    """
    # 检查用户是否已存在
    user = crud_user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在",
        )
    # 创建新用户
    user = crud_user.create(db, obj_in=user_in)
    # 生成访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/wx-login", response_model=Token)
async def wx_login(request: WxLoginRequest, db: Session = Depends(get_db)):
    """
    微信小程序登录
    
    Args:
        request: 包含code的请求体
        db: 数据库会话
        
    Returns:
        Token: 包含access_token的响应
    """
    # 1. 调用微信API获取openid和session_key
    wx_session = await get_wx_session(request.code)
    openid = wx_session["openid"]
    
    # 2. 查找或创建用户
    user = crud_user.get_by_wx_openid(db, wx_openid=openid)
    if not user:
        # 如果用户不存在，创建一个新用户
        user_in = UserCreate(
            username=f"wx_{openid[:8]}",  # 使用openid前8位作为临时用户名
            password=f"wx_{openid[-8:]}",  # 使用openid后8位作为临时密码
            wx_openid=openid,
            role="customer",  # 默认为普通用户
            is_active=True
        )
        user = crud_user.create(db, obj_in=user_in)
    
    # 3. 生成访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }