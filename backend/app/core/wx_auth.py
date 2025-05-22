import httpx
from fastapi import HTTPException, status
from app.core.config import settings

async def get_wx_session(code: str) -> dict:
    """
    调用微信服务器获取session_key和openid
    
    Args:
        code: 微信登录时获取的code
        
    Returns:
        dict: 包含session_key和openid的字典
        
    Raises:
        HTTPException: 当调用微信API失败时抛出
    """
    url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": settings.WX_APP_ID,
        "secret": settings.WX_APP_SECRET,
        "js_code": code,
        "grant_type": "authorization_code"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()
            
            if "errcode" in data and data["errcode"] != 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"微信登录失败: {data.get('errmsg', '未知错误')}"
                )
                
            return {
                "openid": data.get("openid"),
                "session_key": data.get("session_key")
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"调用微信服务器失败: {str(e)}"
        ) 