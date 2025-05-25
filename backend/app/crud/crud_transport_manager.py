from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.models.transport_manager import TransportManager, TransportRole, DriverStatus
from app.models.user import User # For type hinting manager object
from app.schemas.transport_manager import TransportManagerCreate, TransportManagerUpdate

class CRUDTransportManager(CRUDBase[TransportManager, TransportManagerCreate, TransportManagerUpdate]):
    def get_by_company_and_manager_user(
        self, db: Session, *, transport_company_id: int, manager_user_id: int
    ) -> Optional[TransportManager]:
        """根据运输公司ID和用户ID获取运输管理人员记录"""
        return db.query(TransportManager).filter(
            TransportManager.transport_company_id == transport_company_id,
            TransportManager.manager_id == manager_user_id
        ).first()

    def get_managers_by_company(
        self, db: Session, *, transport_company_id: int, skip: int = 0, limit: int = 100
    ) -> List[TransportManager]:
        """获取某个运输公司的所有管理人员 (包括司机、调度员、主管理员)"""
        return db.query(TransportManager).filter(
            TransportManager.transport_company_id == transport_company_id
        ).offset(skip).limit(limit).all()

    def get_drivers_by_company(
        self, db: Session, *, transport_company_id: int, status: Optional[DriverStatus] = None, skip: int = 0, limit: int = 100
    ) -> List[TransportManager]:
        """获取运输公司的所有司机，可选按状态过滤"""
        query = db.query(TransportManager).filter(
            TransportManager.transport_company_id == transport_company_id,
            TransportManager.role == TransportRole.DRIVER
        )
        if status:
            query = query.filter(TransportManager.driver_status == status)
        return query.offset(skip).limit(limit).all()
    
    def get_dispatchers_by_company(
        self, db: Session, *, transport_company_id: int, skip: int = 0, limit: int = 100
    ) -> List[TransportManager]:
        """获取运输公司的所有调度员"""
        return db.query(TransportManager).filter(
            TransportManager.transport_company_id == transport_company_id,
            TransportManager.role == TransportRole.DISPATCHER
        ).offset(skip).limit(limit).all()

    def get_primary_manager_for_company(self, db: Session, *, transport_company_id: int) -> Optional[TransportManager]:
        """获取运输公司的主要管理员"""
        return db.query(TransportManager).filter(
            TransportManager.transport_company_id == transport_company_id,
            TransportManager.is_primary == True
        ).first()

    def create_manager_for_company(
        self, db: Session, *, obj_in: TransportManagerCreate # manager_id is User.id
    ) -> TransportManager:
        """为运输公司创建管理人员 (调度员或司机或主管理员)"""
        existing_assoc = self.get_by_company_and_manager_user(
            db, transport_company_id=obj_in.transport_company_id, manager_user_id=obj_in.manager_id
        )
        if existing_assoc:
            raise ValueError(f"User {obj_in.manager_id} is already associated with transport company {obj_in.transport_company_id}")

        if obj_in.is_primary:
            current_primary = self.get_primary_manager_for_company(db, transport_company_id=obj_in.transport_company_id)
            if current_primary:
                raise ValueError(f"Company {obj_in.transport_company_id} already has a primary manager (User ID: {current_primary.manager_id}).")
            if obj_in.role is not None: # Primary manager should not have a specific role like DRIVER/DISPATCHER
                raise ValueError("Primary manager role must be None.")
        elif obj_in.role is None:
            raise ValueError("Non-primary manager must have a role (DRIVER or DISPATCHER).")
        
        # Specific validations for DRIVER role
        if obj_in.role == TransportRole.DRIVER:
            if not obj_in.driver_license_number:
                raise ValueError("Driver role requires a driver_license_number.")
            # driver_status is defaulted in schema if not provided
        else: # Not a driver, so driver-specific fields should be None or not set
            if obj_in.driver_license_number is not None or obj_in.driver_status != DriverStatus.AVAILABLE: # available is default
                # Ensure default is used or field is None if not driver
                pass # Or raise error if they are set for non-drivers

        return super().create(db, obj_in=obj_in)

    def update_driver_status(
        self, db: Session, *, db_obj: TransportManager, status: DriverStatus
    ) -> TransportManager:
        """更新司机的状态 (db_obj must be a DRIVER)"""
        if db_obj.role != TransportRole.DRIVER:
            raise ValueError("Cannot update driver status for a non-driver role.")
        updated_driver = super().update(db, db_obj=db_obj, obj_in={"driver_status": status})
        return updated_driver

transport_manager = CRUDTransportManager(TransportManager) 