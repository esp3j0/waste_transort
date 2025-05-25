from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session, joinedload
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException # Import HTTPException

from app.crud.base import CRUDBase
from app.models.recycling_manager import RecyclingManager, RecyclingRole
from app.models.user import User # For type hinting manager object
from app.models.recycling_company import RecyclingCompany # For type hinting company object
from app.schemas.recycling_manager import RecyclingManagerCreate, RecyclingManagerUpdate

class CRUDRecyclingManager(CRUDBase[RecyclingManager, RecyclingManagerCreate, RecyclingManagerUpdate]):
    def get_by_company_and_manager_user(
        self, db: Session, *, recycling_company_id: int, manager_user_id: int # Renamed manager_id
    ) -> Optional[RecyclingManager]:
        """根据回收公司ID和用户ID获取回收管理人员记录"""
        return db.query(RecyclingManager).filter(
            RecyclingManager.recycling_company_id == recycling_company_id,
            RecyclingManager.manager_id == manager_user_id # Updated to manager_user_id
        ).first()

    def get_managers_by_company(
        self, db: Session, *, recycling_company_id: int, skip: int = 0, limit: int = 100
    ) -> List[RecyclingManager]:
        """获取某个回收公司的所有管理人员""" # Renamed from get_by_company
        return db.query(RecyclingManager).filter(RecyclingManager.recycling_company_id == recycling_company_id).offset(skip).limit(limit).all()

    def get_by_manager_user(
        self, db: Session, *, manager_user_id: int, skip: int = 0, limit: int = 100
    ) -> List[RecyclingManager]:
        """获取某个用户关联的所有回收管理角色"""
        return db.query(RecyclingManager).filter(RecyclingManager.manager_id == manager_user_id).offset(skip).limit(limit).all()

    def create_manager_for_company(
        self, db: Session, *, obj_in: RecyclingManagerCreate # Takes RecyclingManagerCreate which includes company_id and manager_id
    ) -> RecyclingManager:
        """为回收公司创建管理人员关联。"""
        # Check if user is already a manager for this company
        existing_manager = self.get_by_company_and_manager_user(
            db, recycling_company_id=obj_in.recycling_company_id, manager_user_id=obj_in.manager_id
        )
        if existing_manager:
            raise HTTPException(status_code=400, detail=f"User {obj_in.manager_id} is already a manager for recycling company {obj_in.recycling_company_id}")

        # If creating a primary manager, ensure no other primary manager exists for this company
        if obj_in.is_primary:
            primary_manager = self.get_primary_manager_for_company(db, property_company_id=obj_in.recycling_company_id)
            if primary_manager:
                raise HTTPException(status_code=400, detail=f"Recycling company {obj_in.recycling_company_id} already has a primary manager (User ID: {primary_manager.manager_id})")
        
        # Schema validator should handle these, but defensive checks can remain or be simplified
        if not obj_in.is_primary and not obj_in.role:
            raise HTTPException(status_code=400, detail="Non-primary managers must have a role assigned.")
        if obj_in.is_primary and obj_in.role:
            raise HTTPException(status_code=400, detail="Primary managers should not have a specific role. Role should be None.")

        return super().create(db=db, obj_in=obj_in) # Use base create method
    
    def update(
        self,
        db: Session,
        *,
        db_obj: RecyclingManager,
        obj_in: Union[RecyclingManagerUpdate, Dict[str, Any]]
    ) -> RecyclingManager:
        """更新回收管理人员信息"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        # If attempting to set as primary, and it was not primary before, check if another primary manager exists
        if update_data.get("is_primary") is True and not db_obj.is_primary:
            company_id = db_obj.recycling_company_id
            other_primary_manager = self.get_primary_manager_for_company(
                db, property_company_id=company_id, exclude_self_id=db_obj.id
            )
            if other_primary_manager:
                raise HTTPException(status_code=400, detail=f"Recycling company {company_id} already has another primary manager (User ID: {other_primary_manager.manager_id}). Cannot set this manager as primary.")
        
        is_primary_after_update = update_data.get("is_primary", db_obj.is_primary)
        role_after_update = update_data.get("role", db_obj.role)

        if not is_primary_after_update and not role_after_update:
             raise HTTPException(status_code=400, detail="Non-primary managers must have a role assigned.")
        
        if is_primary_after_update and role_after_update is not None: # Check if role is explicitly set for a primary manager
            raise HTTPException(status_code=400, detail="Primary managers should not have a specific role. Role should be None or not set.")

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def get_primary_manager_for_company(
        self, db: Session, *, property_company_id: int, exclude_self_id: Optional[int] = None
    ) -> Optional[RecyclingManager]:
        """获取回收公司的主要管理员，可选排除某个ID (用于更新检查)"""
        query = db.query(RecyclingManager).filter(
            RecyclingManager.recycling_company_id == property_company_id,
            RecyclingManager.is_primary == True
        )
        if exclude_self_id:
            query = query.filter(RecyclingManager.id != exclude_self_id)
        return query.first()

recycling_manager = CRUDRecyclingManager(RecyclingManager)
