from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.crud.base import CRUDBase
from app.models.property import Property
from app.models.property_manager import PropertyManager
from app.schemas.property import PropertyCreate, PropertyUpdate

class CRUDProperty(CRUDBase[Property, PropertyCreate, PropertyUpdate]):
    """物业CRUD操作"""
    
    def create_with_manager(
        self, db: Session, *, obj_in: PropertyCreate, manager_id: int
    ) -> Property:
        """创建物业并设置管理员"""
        db_obj = Property(**obj_in.model_dump())
        db.add(db_obj)
        db.flush()  # 获取ID
        
        # 创建主要管理员关联
        manager = PropertyManager(
            property_id=db_obj.id,
            manager_id=manager_id,
            role="主要管理员",
            is_primary=True
        )
        db.add(manager)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_manager(
        self, db: Session, *, manager_id: int, skip: int = 0, limit: int = 100
    ) -> List[Property]:
        """获取管理员管理的所有物业"""
        return (
            db.query(self.model)
            .join(PropertyManager)
            .filter(PropertyManager.manager_id == manager_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

property = CRUDProperty(Property)