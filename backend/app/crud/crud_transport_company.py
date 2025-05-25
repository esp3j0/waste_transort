from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session, joinedload
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.models.transport_company import TransportCompany
from app.models.transport_manager import TransportManager # For querying managers of a company
from app.schemas.transport_company import TransportCompanyCreate, TransportCompanyUpdate

class CRUDTransportCompany(CRUDBase[TransportCompany, TransportCompanyCreate, TransportCompanyUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[TransportCompany]:
        """根据运输公司名称获取信息"""
        return db.query(TransportCompany).filter(TransportCompany.name == name).first()

    def create_with_owner(
        self, db: Session, *, obj_in: TransportCompanyCreate, owner_id: int
    ) -> TransportCompany:
        """
        创建运输公司，并指定一个所有者（用户ID）作为主要管理员。
        注意：这只是创建公司。实际的TransportManager记录（将用户设为主要管理员）
        需要在调用此方法后单独创建，或在一个更高级别的服务函数中处理。
        """
        # obj_in_data = jsonable_encoder(obj_in)
        # db_obj = self.model(**obj_in_data) 
        # # owner_id is not directly on TransportCompany model, it's via TransportManager
        # db.add(db_obj)
        # db.commit()
        # db.refresh(db_obj)
        # return db_obj
        # Simplified: super().create will handle it. Owner linking is separate.
        return super().create(db, obj_in=obj_in)


    # Add other specific query methods if needed, e.g., filter by active status, etc.
    # def get_multi_active(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[TransportCompany]:
    #     return db.query(self.model).filter(TransportCompany.is_active == True).offset(skip).limit(limit).all()

transport_company = CRUDTransportCompany(TransportCompany) 