from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
import datetime
import uuid

from app.crud.base import CRUDBase
from app.models.order import Order, OrderStatus
from app.models.property import Property
from app.models.property_manager import PropertyManager
from app.schemas.order import OrderCreate, OrderUpdate

class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    def get_by_order_number(self, db: Session, *, order_number: str) -> Optional[Order]:
        """根据订单编号获取订单"""
        return db.query(Order).filter(Order.order_number == order_number).first()
    
    def get_by_customer(self, db: Session, *, customer_id: int, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Order]:
        """获取客户的所有订单"""
        query = db.query(Order).filter(Order.customer_id == customer_id)
        if status:
            query = query.filter(Order.status == status)
        return query.offset(skip).limit(limit).all()
    
    def get_by_property_manager(self, db: Session, *, manager_id: int, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Order]:
        """获取物业管理员负责的所有订单"""
        # 获取管理员管理的所有物业
        managed_properties = (
            db.query(Property)
            .join(PropertyManager)
            .filter(PropertyManager.manager_id == manager_id)
            .all()
        )
        property_ids = [p.id for p in managed_properties]
        
        # 获取这些物业的所有订单
        query = db.query(Order).filter(Order.property_id.in_(property_ids))
        if status:
            query = query.filter(Order.status == status)
        return query.offset(skip).limit(limit).all()
    
    def get_by_transport_manager(self, db: Session, *, manager_id: int, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Order]:
        """获取运输管理员负责的所有订单"""
        query = db.query(Order).filter(Order.transport_manager_id == manager_id)
        if status:
            query = query.filter(Order.status == status)
        return query.offset(skip).limit(limit).all()
    
    def get_by_recycling_manager(self, db: Session, *, manager_id: int, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Order]:
        """获取回收站管理员负责的所有订单"""
        query = db.query(Order).filter(Order.recycling_manager_id == manager_id)
        if status:
            query = query.filter(Order.status == status)
        return query.offset(skip).limit(limit).all()
    
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
    
    def create_with_customer(self, db: Session, *, obj_in: OrderCreate, customer_id: int) -> Order:
        """创建订单并关联客户ID"""
        obj_in_data = jsonable_encoder(obj_in)
        # 生成唯一订单编号
        current_time = datetime.datetime.now()
        order_number = f"ORD-{current_time.strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        db_obj = Order(**obj_in_data, customer_id=customer_id, order_number=order_number)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Order]:
        """获取多个订单，支持状态过滤"""
        query = db.query(self.model)
        if status:
            query = query.filter(Order.status == status)
        return query.offset(skip).limit(limit).all()

order = CRUDOrder(Order)