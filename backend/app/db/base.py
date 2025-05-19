# 导入所有模型，以便Alembic可以自动检测
from app.db.base_class import Base
from app.models.user import User
from app.models.order import Order
from app.models.property import Property
from app.models.transport import Transport
from app.models.recycling import Recycling