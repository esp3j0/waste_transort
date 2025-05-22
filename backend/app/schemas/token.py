from pydantic import BaseModel


class Token(BaseModel):
    """用于OAuth2认证的令牌模型"""
    access_token: str
    token_type: str