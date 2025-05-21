import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db
from main import app

# 使用SQLite内存数据库进行测试
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    # 创建测试数据库表
    Base.metadata.create_all(bind=engine)
    
    # 创建数据库会话
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    
    # 清理测试数据库
    Base.metadata.drop_all(bind=engine)