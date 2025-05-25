from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.models.waste_record import WasteRecord
from app.schemas.waste_record import WasteRecordCreate, WasteRecordUpdate

class CRUDWasteRecord(CRUDBase[WasteRecord, WasteRecordCreate, WasteRecordUpdate]):
    def create_with_order_and_user(
        self, db: Session, *, obj_in: WasteRecordCreate, order_id: int, user_id: Optional[int] = None
    ) -> WasteRecord:
        """
        创建废物记录，关联到订单和可选的记录用户。
        注意: obj_in.order_id 应该与参数 order_id 一致，这里我们信任调用者或在API层校验。
        """
        create_data = obj_in.model_dump()
        create_data['order_id'] = order_id # Ensure order_id is correctly set
        if user_id:
            create_data['recorded_by_user_id'] = user_id
        
        db_obj = WasteRecord(**create_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_order_id(
        self, db: Session, *, order_id: int, skip: int = 0, limit: int = 100
    ) -> List[WasteRecord]:
        """根据订单ID获取所有废物记录"""
        return (
            db.query(self.model)
            .filter(WasteRecord.order_id == order_id)
            .options(joinedload(self.model.recorded_by_user)) # Eager load user
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_with_user(self, db: Session, *, id: int) -> Optional[WasteRecord]:
        """获取单个废物记录，并预加载用户信息"""
        return (
            db.query(self.model)
            .options(joinedload(self.model.recorded_by_user))
            .filter(self.model.id == id)
            .first()
        )

waste_record = CRUDWasteRecord(WasteRecord)
