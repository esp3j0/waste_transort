from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.models.address import Address
from app.schemas.address import AddressCreate, AddressUpdate

class CRUDAddress(CRUDBase[Address, AddressCreate, AddressUpdate]):
    def create_with_user(
        self, db: Session, *, obj_in: AddressCreate, user_id: int
    ) -> Address:
        """为用户创建新地址"""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Address]:
        """获取用户的所有地址"""
        return (
            db.query(self.model)
            .filter(Address.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_default_address(
        self, db: Session, *, user_id: int
    ) -> Optional[Address]:
        """获取用户的默认地址"""
        return (
            db.query(self.model)
            .filter(Address.user_id == user_id, Address.is_default == True)
            .first()
        )

    def set_default_address(
        self, db: Session, *, address_id: int, user_id: int
    ) -> Address:
        """设置默认地址"""
        # 先将用户的所有地址设置为非默认
        db.query(self.model).filter(
            Address.user_id == user_id
        ).update({"is_default": False})
        
        # 将指定地址设置为默认
        address = db.query(self.model).filter(
            Address.id == address_id,
            Address.user_id == user_id
        ).first()
        if address:
            address.is_default = True
            db.add(address)
            db.commit()
            db.refresh(address)
        return address

address = CRUDAddress(Address) 