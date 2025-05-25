from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token
from app.core.wx_auth import get_wx_session
from app.db.session import get_db
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserCreateOpen, UserResponse
from app.schemas.auth import WxLoginRequest
from app.crud.crud_user import user as crud_user
from app.models.user import UserRole

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """
    获取OAuth2兼容的令牌，用于用户登录
    """
    user_obj = crud_user.authenticate(db, username=form_data.username, password=form_data.password)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user_obj.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户未激活")
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    user_response = UserResponse.model_validate(user_obj).model_dump()
    return {
        "access_token": create_access_token(
            user_obj.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "user": user_response
    }

@router.post("/register", response_model=Token)
async def register_user(user_in: UserCreateOpen, db: Session = Depends(get_db)):
    """
    注册新用户并返回访问令牌和用户信息
    """
    existing_user = crud_user.get_by_username(db, username=user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在",
        )
    
    if user_in.phone:
        existing_phone_user = crud_user.get_by_phone(db, phone=user_in.phone)
        if existing_phone_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已被注册"
            )

    if user_in.email:
        existing_email_user = crud_user.get_by_email(db, email=user_in.email)
        if existing_email_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )

    user_create_data = UserCreate(
        username=user_in.username,
        password=user_in.password,
        email=user_in.email,
        full_name=user_in.full_name,
        phone=user_in.phone,
        role=UserRole.CUSTOMER,
        is_superuser=False,
        is_active=True
    )
    
    new_user_obj = crud_user.create(db, obj_in=user_create_data)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    user_response = UserResponse.model_validate(new_user_obj).model_dump()
    return {
        "access_token": create_access_token(
            new_user_obj.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "user": user_response
    }

@router.post("/wx-login", response_model=Token)
async def wx_login(request: WxLoginRequest, db: Session = Depends(get_db)):
    """
    微信小程序登录
    """
    wx_session = await get_wx_session(request.code)
    openid = wx_session.get("openid")
    if not openid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to get openid from WeChat")
    
    user_obj = crud_user.get_by_wx_openid(db, wx_openid=openid)
    if not user_obj:
        user_create_in = UserCreate(
            username=f"wx_{openid[:12]}",
            password=openid,
            wx_openid=openid,
            role=UserRole.CUSTOMER,
            is_active=True,
            full_name=f"微信用户{openid[:4]}"
        )
        user_obj = crud_user.create(db, obj_in=user_create_in)
    elif not user_obj.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户未激活")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    user_response = UserResponse.model_validate(user_obj).model_dump()
    return {
        "access_token": create_access_token(
            user_obj.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "user": user_response
    }