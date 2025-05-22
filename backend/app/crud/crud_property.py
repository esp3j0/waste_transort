from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.crud.base import CRUDBase
from app.models.property import Property
from app.models.property_manager import PropertyManager
from app.schemas.property import PropertyCreate, PropertyUpdate, PropertyManagerCreate, PropertyManagerUpdate

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
    
    def add_manager(
        self, db: Session, *, property_id: int, obj_in: PropertyManagerCreate
    ) -> PropertyManager:
        """添加物业管理员"""
        # 检查是否已存在主要管理员
        if obj_in.is_primary:
            existing_primary = (
                db.query(PropertyManager)
                .filter(
                    and_(
                        PropertyManager.property_id == property_id,
                        PropertyManager.is_primary == True
                    )
                )
                .first()
            )
            if existing_primary:
                raise ValueError("已存在主要管理员")
        
        # 创建管理员关联
        db_obj = PropertyManager(
            property_id=property_id,
            manager_id=obj_in.manager_id,
            role=obj_in.role,
            is_primary=obj_in.is_primary
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_manager(
        self, db: Session, *, manager_id: int, obj_in: PropertyManagerUpdate
    ) -> PropertyManager:
        """更新物业管理员信息"""
        db_obj = db.query(PropertyManager).filter(PropertyManager.id == manager_id).first()
        if not db_obj:
            raise ValueError("管理员不存在")
        
        # 如果要设置为主要管理员，检查是否已存在
        if obj_in.is_primary and not db_obj.is_primary:
            existing_primary = (
                db.query(PropertyManager)
                .filter(
                    and_(
                        PropertyManager.property_id == db_obj.property_id,
                        PropertyManager.is_primary == True
                    )
                )
                .first()
            )
            if existing_primary:
                raise ValueError("已存在主要管理员")
        
        # 更新管理员信息
        for field, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove_manager(self, db: Session, *, manager_id: int) -> None:
        """移除物业管理员"""
        db_obj = db.query(PropertyManager).filter(PropertyManager.id == manager_id).first()
        if not db_obj:
            raise ValueError("管理员不存在")
        
        # 不允许删除主要管理员
        if db_obj.is_primary:
            raise ValueError("不能删除主要管理员")
        
        db.delete(db_obj)
        db.commit()
    
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