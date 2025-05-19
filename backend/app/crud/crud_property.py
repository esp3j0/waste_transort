from typing import List, Optional, Dict, Union, Any
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.property import Property
from app.schemas.property import PropertyCreate, PropertyUpdate

class CRUDProperty(CRUDBase[Property, PropertyCreate, PropertyUpdate]):
    def create_with_manager(self, db: Session, *, obj_in: PropertyCreate, manager_id: int) -> Property:
        """创建物业信息并关联管理员"""
        obj_in_data = obj_in.dict()
        db_obj = Property(**obj_in_data, manager_id=manager_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_manager(self, db: Session, *, manager_id: int, skip: int = 0, limit: int = 100) -> List[Property]:
        """获取指定管理员的物业信息"""
        return db.query(self.model).filter(Property.manager_id == manager_id).offset(skip).limit(limit).all()
    
    def get_by_community(self, db: Session, *, community_name: str) -> List[Property]:
        """根据小区名称获取物业信息"""
        return db.query(self.model).filter(Property.community_name == community_name).all()

property = CRUDProperty(Property)