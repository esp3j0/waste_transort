from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session, joinedload
from fastapi.encoders import jsonable_encoder
import datetime
import uuid

from app.crud.base import CRUDBase
from app.models.order import Order, OrderStatus
from app.models.property_manager import PropertyManager
from app.models.address import Address
from app.models.community import Community
from app.models.transport_manager import TransportManager
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
        return query.options(joinedload(Order.address).joinedload(Address.community)).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_property_manager(
        self, db: Session, *, manager_user_id: int, skip: int = 0, limit: int = 100, status: Optional[str] = None
    ) -> List[Order]:
        """获取物业管理员（主要或非主要）相关的订单列表"""
        
        property_manager_records = db.query(PropertyManager).filter(PropertyManager.manager_id == manager_user_id).all()
        
        if not property_manager_records:
            return []

        accessible_community_ids = set()

        for pm_record in property_manager_records:
            if pm_record.is_primary:
                # 主要管理员：获取其物业公司管理的所有小区ID
                if pm_record.property_company_id:
                    # property_obj = db.query(Property).filter(Property.id == pm_record.property_id).options(joinedload(Property.communities)).first()
                    # Query communities directly associated with the property
                    communities_of_property = db.query(Community.id).filter(Community.property_company_id == pm_record.property_company_id).all()
                    for comm_id_tuple in communities_of_property:
                        accessible_community_ids.add(comm_id_tuple[0])
            else:
                # 非主要管理员：获取其直接关联的小区ID
                if pm_record.community_id:
                    accessible_community_ids.add(pm_record.community_id)
        
        if not accessible_community_ids:
            return []
        
        # 查询这些小区下的所有地址ID
        # address_ids_query = db.query(Address.id).filter(Address.community_id.in_(list(accessible_community_ids)))
        # address_ids = [addr_id_tuple[0] for addr_id_tuple in address_ids_query.all()]
        # if not address_ids:
        #     return []

        # 查询这些地址关联的订单
        # query = db.query(Order).filter(Order.address_id.in_(address_ids))
        
        # Optimized query: Join Order -> Address -> Community and filter by community_ids
        query = (
            db.query(Order)
            .join(Order.address)
            .filter(Address.community_id.in_(list(accessible_community_ids)))
        )

        if status:
            query = query.filter(Order.status == status)
        
        return query.options(joinedload(Order.address).joinedload(Address.community)).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_transport_manager(self, db: Session, *, manager_id: int, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Order]:
        """获取运输管理员负责的所有订单"""
        query = db.query(Order).filter(Order.transport_manager_id == manager_id)
        if status:
            query = query.filter(Order.status == status)
        return query.options(joinedload(Order.address).joinedload(Address.community)).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_recycling_manager(self, db: Session, *, manager_id: int, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Order]:
        """获取回收站管理员负责的所有订单"""
        query = db.query(Order).filter(Order.recycling_manager_id == manager_id)
        if status:
            query = query.filter(Order.status == status)
        return query.options(joinedload(Order.address).joinedload(Address.community)).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_driver(self, db: Session, *, driver_manager_assoc_id: int, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Order]:
        """获取司机负责的所有订单 (通过 TransportManager.id)"""
        # Order.driver_id has been replaced by Order.driver_assoc_id which links to TransportManager.id
        query = db.query(Order).filter(Order.driver_assoc_id == driver_manager_assoc_id)
        if status:
            query = query.filter(Order.status == status)
        return query.options(
            joinedload(Order.address).joinedload(Address.community),
            joinedload(Order.transport_company),
            joinedload(Order.vehicle)
        ).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_transport_company(self, db: Session, *, transport_company_id: int, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Order]:
        """获取指定运输公司处理的所有订单"""
        query = db.query(Order).filter(Order.transport_company_id == transport_company_id)
        if status:
            query = query.filter(Order.status == status)
        return query.options(
            joinedload(Order.address).joinedload(Address.community),
            joinedload(Order.driver_association).joinedload(TransportManager.manager), # Load driver's user details
            joinedload(Order.vehicle)
        ).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_recycling_company(self, db: Session, *, recycling_company_id: int, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Order]:
        """获取回收公司的所有订单"""
        query = db.query(Order).filter(Order.recycling_company_id == recycling_company_id)
        if status:
            query = query.filter(Order.status == status)
        return query.options(joinedload(Order.address).joinedload(Address.community)).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_status(self, db: Session, *, status: str, skip: int = 0, limit: int = 100) -> List[Order]:
        """根据状态获取订单"""
        return db.query(Order).filter(Order.status == status).options(joinedload(Order.address).joinedload(Address.community)).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    def update_status(self, db: Session, *, db_obj: Order, status: str, **kwargs) -> Order:
        """更新订单状态"""
        update_data = {"status": status}
        # Ensure datetime is set for specific status updates if provided in kwargs
        if status == OrderStatus.PROPERTY_CONFIRMED and "property_confirm_time" not in kwargs:
            kwargs["property_confirm_time"] = datetime.datetime.utcnow()
        elif status == OrderStatus.DELIVERED and "delivery_time" not in kwargs:
            kwargs["delivery_time"] = datetime.datetime.utcnow()
        elif status == OrderStatus.RECYCLING_CONFIRMED and "recycling_confirm_time" not in kwargs:
            kwargs["recycling_confirm_time"] = datetime.datetime.utcnow()
        # Add more specific time updates for other statuses if needed

        update_data.update(kwargs)
        return super().update(db, db_obj=db_obj, obj_in=update_data)
    
    def create_with_customer(self, db: Session, *, obj_in: OrderCreate, customer_id: int) -> Order:
        """创建订单并关联客户ID"""
        obj_in_data = jsonable_encoder(obj_in)
        # 生成唯一订单编号
        current_time = datetime.datetime.now() # Use datetime.datetime.now(datetime.timezone.utc) for timezone aware
        order_number = f"ORD-{current_time.strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        # Ensure address exists and is valid
        address_obj = db.query(Address).filter(Address.id == obj_in.address_id, Address.user_id == customer_id).first()
        if not address_obj:
            raise ValueError(f"无效的地址ID: {obj_in.address_id} 或该地址不属于用户 {customer_id}")

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
        return query.options(joinedload(Order.address).joinedload(Address.community)).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()

order = CRUDOrder(Order)