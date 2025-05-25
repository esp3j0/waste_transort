from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.crud.base import CRUDBase
from app.models.property_company import PropertyCompany # 新模型
from app.models.property_manager import PropertyManager
from app.schemas.property_company import PropertyCompanyCreate, PropertyCompanyUpdate # 新schemas

class CRUDPropertyCompany(CRUDBase[PropertyCompany, PropertyCompanyCreate, PropertyCompanyUpdate]): # 重命名类
    """物业公司CRUD操作""" # 更新描述
    
    def create_with_primary_manager(
        self, db: Session, *, obj_in: PropertyCompanyCreate, manager_user_id: int
    ) -> PropertyCompany:
        """创建物业公司并设置主要管理员""" # 更新描述
        db_obj = PropertyCompany(**obj_in.model_dump()) # 使用新模型
        db.add(db_obj)
        db.flush()  # 获取ID
        
        # 创建主要管理员关联 (PropertyManager)
        # 注意: PropertyManagerCreate schema 应该包含 property_company_id
        # property_manager.py CRUD应该有一个 create_with_company_and_user 方法或类似方法
        # 这里为了简化，直接创建 PropertyManager 对象，但在实际项目中应使用其CRUD和schema
        manager_assoc = PropertyManager(
            property_company_id=db_obj.id, # 更新外键字段名
            manager_id=manager_user_id,
            role="主要管理员", # 或者使用枚举
            is_primary=True
        )
        db.add(manager_assoc)
        db.commit()
        db.refresh(db_obj) # 刷新物业公司对象以包含关系
        return db_obj
    
    def get_by_manager_user(
        self, db: Session, *, manager_user_id: int, skip: int = 0, limit: int = 100
    ) -> List[PropertyCompany]:
        """获取用户管理的所有物业公司""" # 更新描述
        return (
            db.query(self.model) # self.model 现在是 PropertyCompany
            .join(PropertyManager, self.model.id == PropertyManager.property_company_id) # 明确join条件
            .filter(PropertyManager.manager_id == manager_user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

property_company = CRUDPropertyCompany(PropertyCompany) # 重命名实例 