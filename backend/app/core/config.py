from typing import List, Optional, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

class Settings(BaseSettings):
    # 基础配置
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "建筑垃圾清理运输系统")
    PROJECT_DESCRIPTION: str = os.getenv("PROJECT_DESCRIPTION", "建筑垃圾清理运输微信小程序后端API")
    VERSION: str = os.getenv("VERSION", "0.1.0")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    
    # 安全配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60*24*8))  # 8天
    
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./waste_transport.db")
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # 微信小程序配置
    WX_APP_ID: str = os.getenv("WX_APP_ID", "")
    WX_APP_SECRET: str = os.getenv("WX_APP_SECRET", "")

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()