import logging
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import engine
from app.core.config import settings
from app.crud.crud_user import user
from app.schemas.user import UserCreate
from app.models.user import UserRole

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 确保所有模型都被导入
from app.models import user, property  # noqa

def init_db(db: Session) -> None:
    """初始化数据库"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 创建超级管理员账户
    create_first_superuser(db)

def create_first_superuser(db: Session) -> None:
    """创建第一个超级管理员账户"""
    # 检查是否已存在超级管理员
    superuser = user.get_by_username(db, username="admin")
    if not superuser:
        logger.info("创建初始超级管理员账户")
        user_in = UserCreate(
            username="admin",
            phone="13800000000",  # 示例手机号
            email="admin@example.com",
            password="admin123",  # 初始密码，应在生产环境中修改
            full_name="系统管理员",
            role=UserRole.ADMIN,
            is_superuser=True
        )
        user.create(db, obj_in=user_in)
        logger.info("超级管理员账户创建成功")
    else:
        logger.info("超级管理员账户已存在，跳过创建")