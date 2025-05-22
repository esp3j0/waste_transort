from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.models.recycling import Recycling, RecyclingStatus
from app.schemas.recycling import RecyclingCreate, RecyclingUpdate

class CRUDRecycling(CRUDBase[Recycling, RecyclingCreate, RecyclingUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Recycling]:
        """根据回收站名称获取回收站信息"""
        return db.query(Recycling).filter(Recycling.name == name).first()
    
    def get_by_recycling_type(self, db: Session, *, recycling_type: str, skip: int = 0, limit: int = 100) -> List[Recycling]:
        """根据回收站类型获取回收站信息"""
        return db.query(Recycling).filter(Recycling.recycling_type == recycling_type).offset(skip).limit(limit).all()
    
    def get_by_status(self, db: Session, *, status: str, skip: int = 0, limit: int = 100) -> List[Recycling]:
        """根据回收站状态获取回收站信息"""
        return db.query(Recycling).filter(Recycling.status == status).offset(skip).limit(limit).all()
    
    def get_by_manager(self, db: Session, *, manager_id: int, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Recycling]:
        """获取管理员负责的所有回收站信息"""
        query = db.query(Recycling).filter(Recycling.manager_id == manager_id)
        if status:
            query = query.filter(Recycling.status == status)
        return query.offset(skip).limit(limit).all()
    
    def get_active_stations(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Recycling]:
        """获取所有正常运营的回收站"""
        return db.query(Recycling).filter(
            Recycling.status == RecyclingStatus.ACTIVE,
            Recycling.is_active == True
        ).offset(skip).limit(limit).all()
    
    def update_status(self, db: Session, *, db_obj: Recycling, status: str) -> Recycling:
        """更新回收站状态"""
        return super().update(db, db_obj=db_obj, obj_in={"status": status})
    
    def update_current_load(self, db: Session, *, db_obj: Recycling, additional_load: float) -> Recycling:
        """更新回收站当前负载"""
        new_load = db_obj.current_load + additional_load
        return super().update(db, db_obj=db_obj, obj_in={"current_load": new_load})
    
    def create_with_manager(self, db: Session, *, obj_in: RecyclingCreate, manager_id: int) -> Recycling:
        """创建回收站信息并关联管理员ID"""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = Recycling(**obj_in_data, manager_id=manager_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

recycling = CRUDRecycling(Recycling)