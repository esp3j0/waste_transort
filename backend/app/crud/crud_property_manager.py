from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.crud.base import CRUDBase
from app.models.property_manager import PropertyManager
from app.schemas.property_manager import PropertyManagerCreate, PropertyManagerUpdate

class CRUDPropertyManager(CRUDBase[PropertyManager, PropertyManagerCreate, PropertyManagerUpdate]):
    def create(self, db: Session, *, obj_in: PropertyManagerCreate) -> PropertyManager:
        """
        创建新的物业管理员关联记录.
        property_company_id is now part of PropertyManagerCreate schema.
        """
        if obj_in.is_primary is False and obj_in.community_id is None:
            raise HTTPException(
                status_code=400,
                detail="非主要管理员必须关联一个小区 (community_id is required for non-primary managers)."
            )
        if obj_in.is_primary is True and obj_in.community_id is not None:
            obj_in.community_id = None

        existing = self.get_by_property_company_and_manager_user(
            db, property_company_id=obj_in.property_company_id, manager_user_id=obj_in.manager_id
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"User {obj_in.manager_id} is already a manager for property company {obj_in.property_company_id}."
            )

        if obj_in.is_primary:
            primary_manager = self.get_primary_manager_for_company(db, property_company_id=obj_in.property_company_id)
            if primary_manager:
                raise HTTPException(
                    status_code=400,
                    detail=f"Property company {obj_in.property_company_id} already has a primary manager (User ID: {primary_manager.manager_id})."
                )

        return super().create(db=db, obj_in=obj_in)

    def update(
        self, db: Session, *, db_obj: PropertyManager, obj_in: Union[PropertyManagerUpdate, Dict[str, Any]]
    ) -> PropertyManager:
        """
        更新物业管理员信息
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        is_primary_final = update_data.get("is_primary", db_obj.is_primary)
        community_id_final = update_data.get("community_id", db_obj.community_id)

        if is_primary_final is False and community_id_final is None:
            if not update_data.get("role"):
                raise HTTPException(
                    status_code=400,
                    detail="非主要管理员必须关联一个小区。"
                )

        if is_primary_final is True:
            update_data["community_id"] = None
        
        if is_primary_final is True and not db_obj.is_primary:
            other_primary_manager = self.get_primary_manager_for_company(
                db, property_company_id=db_obj.property_company_id, exclude_self_id=db_obj.id
            )
            if other_primary_manager:
                raise HTTPException(
                    status_code=400,
                    detail=f"Property company {db_obj.property_company_id} already has another primary manager (User ID: {other_primary_manager.manager_id}). Cannot set this manager as primary."
                )

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def get_by_property_company_and_manager_user(
        self, db: Session, *, property_company_id: int, manager_user_id: int
    ) -> Optional[PropertyManager]:
        return db.query(PropertyManager).filter(
            PropertyManager.property_company_id == property_company_id,
            PropertyManager.manager_id == manager_user_id
        ).first()

    def get_managers_by_company(
        self, db: Session, *, property_company_id: int, skip: int = 0, limit: int = 100
    ) -> List[PropertyManager]:
        """获取某个物业公司的所有管理人员"""
        return db.query(PropertyManager).filter(
            PropertyManager.property_company_id == property_company_id
        ).offset(skip).limit(limit).all()

    def get_primary_manager_for_company(
        self, db: Session, *, property_company_id: int, exclude_self_id: Optional[int] = None
    ) -> Optional[PropertyManager]:
        """获取物业公司的主要管理员，可选排除某个ID (用于更新检查)"""
        query = db.query(PropertyManager).filter(
            PropertyManager.property_company_id == property_company_id,
            PropertyManager.is_primary == True
        )
        if exclude_self_id:
            query = query.filter(PropertyManager.id != exclude_self_id)
        return query.first()

property_manager = CRUDPropertyManager(PropertyManager) 