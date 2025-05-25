from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.models.vehicle import Vehicle, VehicleStatus, VehicleType
from app.schemas.vehicle import VehicleCreate, VehicleUpdate

class CRUDVehicle(CRUDBase[Vehicle, VehicleCreate, VehicleUpdate]):
    def get_by_plate_number(self, db: Session, *, plate_number: str) -> Optional[Vehicle]:
        """根据车牌号获取车辆信息"""
        return db.query(Vehicle).filter(Vehicle.plate_number == plate_number).first()

    def get_by_transport_company(
        self, db: Session, *, transport_company_id: int, skip: int = 0, limit: int = 100
    ) -> List[Vehicle]:
        """获取某个运输公司的所有车辆"""
        return db.query(Vehicle).filter(Vehicle.transport_company_id == transport_company_id).offset(skip).limit(limit).all()

    def get_vehicles_by_status(
        self, db: Session, *, transport_company_id: int, status: VehicleStatus, skip: int = 0, limit: int = 100
    ) -> List[Vehicle]:
        """获取运输公司特定状态的所有车辆"""
        return db.query(Vehicle).filter(
            Vehicle.transport_company_id == transport_company_id,
            Vehicle.status == status
        ).offset(skip).limit(limit).all()

    def create_for_company(self, db: Session, *, obj_in: VehicleCreate, transport_company_id: int) -> Vehicle:
        """为指定的运输公司创建车辆"""
        # Ensure plate_number is unique before creating
        existing_vehicle = self.get_by_plate_number(db, plate_number=obj_in.plate_number)
        if existing_vehicle:
            raise ValueError(f"Vehicle with plate number {obj_in.plate_number} already exists.")
        
        # obj_in_data = jsonable_encoder(obj_in)
        # db_obj = self.model(**obj_in_data, transport_company_id=transport_company_id)
        # The transport_company_id is already in VehicleCreate schema
        return super().create(db, obj_in=obj_in)
    
    def update_vehicle_status(self, db: Session, *, db_obj: Vehicle, status: VehicleStatus) -> Vehicle:
        """更新车辆的状态"""
        return super().update(db, db_obj=db_obj, obj_in={"status": status})

vehicle = CRUDVehicle(Vehicle) 