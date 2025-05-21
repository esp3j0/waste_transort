from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.order import Order, OrderStatus
from app.schemas.order import OrderCreate, OrderUpdate

class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    def get_by_order_number(self, db: Session, *, order_number: str) -> Optional[Order]:
        """根据订单编号获取订单"""
        return db.query(Order).filter(Order.order_number == order_number).first()
    
    def get_by_customer(self, db: Session, *, customer_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        """获取客户的所有订单"""
        return db.query(Order).filter(Order.customer_id == customer_id).offset(skip).limit(limit).all()
    
    def get_by_property_manager(self, db: Session, *, property_manager_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        """获取物业管理员负责的所有订单"""
        return db.query(Order).filter(Order.property_manager_id == property_manager_id).offset(skip).limit(limit).all()
    
    def get_by_transport_manager(self, db: Session, *, transport_manager_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        """获取运输管理员负责的所有订单"""
        return db.query(Order).filter(Order.transport_manager_id == transport_manager_id).offset(skip).limit(limit).all()
    
    def get_by_recycling_manager(self, db: Session, *, recycling_manager_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        """获取回收站管理员负责的所有订单"""
        return db.query(Order).filter(Order.recycling_manager_id == recycling_manager_id).offset(skip).limit(limit).all()
    
    def get_by_driver(self, db: Session, *, driver_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        """获取司机负责的所有订单"""
        return db.query(Order).filter(Order.driver_id == driver_id).offset(skip).limit(limit).all()
    
    def get_by_recycling_station(self, db: Session, *, recycling_station_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        """获取回收站的所有订单"""
        return db.query(Order).filter(Order.recycling_station_id == recycling_station_id).offset(skip).limit(limit).all()
    
    def get_by_status(self, db: Session, *, status: str, skip: int = 0, limit: int = 100) -> List[Order]:
        """根据状态获取订单"""
        return db.query(Order).filter(Order.status == status).offset(skip).limit(limit).all()
    
    def update_status(self, db: Session, *, db_obj: Order, status: str, **kwargs) -> Order:
        """更新订单状态"""
        update_data = {"status": status}
        update_data.update(kwargs)
        return super().update(db, db_obj=db_obj, obj_in=update_data)

order = CRUDOrder(Order)