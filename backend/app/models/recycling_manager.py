from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base_class import Base
# from app.models.user import User # 确保 User 模型可以被导入, 如果 User 模型中没有反向关系则不用显式导入

class RecyclingRole(str, enum.Enum):
    """回收端人员角色枚举"""
    POUNDER = "pounder"      # 过磅员
    SUPERVISOR = "supervisor"  # 主管 (如果除了 is_primary 外还需要区分普通主管)
    # 主管理员通过 is_primary 字段标识，所以这里可以不定义 ADMIN 或 PRIMARY_MANAGER
    # 如果有其他特定角色，在此添加

class RecyclingManager(Base):
    """回收管理人员模型 (关联用户、回收公司和角色)"""
    __tablename__ = "recycling_manager"

    id = Column(Integer, primary_key=True, index=True)
    recycling_company_id = Column(Integer, ForeignKey("recycling_company.id"), nullable=False)
    manager_id = Column(Integer, ForeignKey("user.id"), nullable=False) # 关联到 User 表的 id
    
    # 角色信息
    # is_primary 为 True 代表该公司最高管理员
    is_primary = Column(Boolean, default=False, nullable=False) 
    # role 仅在 is_primary 为 False 时有意义，用于区分不同类型的员工，如过磅员
    role = Column(SAEnum(RecyclingRole), nullable=True) 
    
    # 其他特定于此角色的字段可以添加在此，例如：
    # work_area = Column(String, nullable=True) # 工作区域/负责的回收线等

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    recycling_company = relationship("RecyclingCompany", back_populates="recycling_managers")
    manager = relationship("User", back_populates="managed_recycling_companies") # User.managed_recycling_companies 需要在 User 模型中定义

    def __repr__(self):
        return f"<RecyclingManager(id={self.id}, company_id={self.recycling_company_id}, user_id={self.manager_id}, role={self.role}, is_primary={self.is_primary})>" 