from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base

# 导入所有模型，确保它们被注册到Base中
from app.models.user import User
from app.models.property import Property
from app.models.order import Order
from app.models.transport import Transport
from app.models.recycling import Recycling

def run_migrations():
    """运行数据库迁移，创建所有表"""
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    Base.metadata.create_all(bind=engine)
    print("数据库迁移完成，所有表已创建")

def reset_database():
    """重置数据库，删除所有表并重新创建"""
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("数据库已重置，所有表已重新创建")

if __name__ == "__main__":
    run_migrations()