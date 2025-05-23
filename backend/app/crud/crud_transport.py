from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.models.transport import Transport, DriverStatus
from app.schemas.transport import TransportCreate, TransportUpdate

class CRUDTransport(CRUDBase[Transport, TransportCreate, TransportUpdate]):
    def get_by_driver_name(self, db: Session, *, driver_name: str) -> Optional[Transport]:
        """根据司机姓名获取运输信息"""
        return db.query(Transport).filter(Transport.driver_name == driver_name).first()
    
    def get_by_vehicle_plate(self, db: Session, *, vehicle_plate: str) -> Optional[Transport]:
        """根据车牌号获取运输信息"""
        return db.query(Transport).filter(Transport.vehicle_plate == vehicle_plate).first()
    
    def get_by_driver_status(self, db: Session, *, status: str, skip: int = 0, limit: int = 100) -> List[Transport]:
        """根据司机状态获取运输信息"""
        return db.query(Transport).filter(Transport.driver_status == status).offset(skip).limit(limit).all()
    
    def get_by_manager(self, db: Session, *, manager_id: int, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Transport]:
        """获取管理员负责的所有运输信息"""
        query = db.query(Transport).filter(Transport.manager_id == manager_id)
        if status:
            query = query.filter(Transport.driver_status == status)
        return query.offset(skip).limit(limit).all()
    
    def get_available_drivers(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Transport]:
        """获取所有可用的司机"""
        return db.query(Transport).filter(
            Transport.driver_status == DriverStatus.AVAILABLE,
            Transport.is_active == True
        ).offset(skip).limit(limit).all()
    
    def update_driver_status(self, db: Session, *, db_obj: Transport, status: str) -> Transport:
        """更新司机状态"""
        return super().update(db, db_obj=db_obj, obj_in={"driver_status": status})
    
    def create_with_manager(self, db: Session, *, obj_in: TransportCreate, manager_id: int) -> Transport:
        """创建运输信息并关联管理员ID"""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = Transport(**obj_in_data, manager_id=manager_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

transport = CRUDTransport(Transport)