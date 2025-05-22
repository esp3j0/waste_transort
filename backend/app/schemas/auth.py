from pydantic import BaseModel

class WxLoginRequest(BaseModel):
    """微信登录请求模型"""
    code: str 