from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from datetime import datetime

from app.crud.base import CRUDBase
from app.models.payment import Payment, PaymentStatus
from app.schemas.payment import PaymentCreate, PaymentUpdate

class CRUDPayment(CRUDBase[Payment, PaymentCreate, PaymentUpdate]):
    def create_for_order(self, db: Session, *, obj_in: PaymentCreate, order_id: int) -> Payment:
        """为指定订单创建支付记录。"""
        create_data = obj_in.model_dump()
        create_data['order_id'] = order_id # Ensure order_id is correct
        
        # Potentially set default status if not provided, though model has default
        if 'status' not in create_data:
            create_data['status'] = PaymentStatus.PENDING
            
        db_obj = Payment(**create_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_order_id(
        self, db: Session, *, order_id: int, skip: int = 0, limit: int = 100
    ) -> List[Payment]:
        """根据订单ID获取所有支付记录"""
        return (
            db.query(self.model)
            .filter(Payment.order_id == order_id)
            .order_by(Payment.initiated_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_transaction_id(self, db: Session, *, transaction_id: str) -> Optional[Payment]:
        """根据交易ID获取支付记录"""
        return db.query(self.model).filter(Payment.transaction_id == transaction_id).first()

    def update_payment_status(
        self, db: Session, *, db_obj: Payment, status: PaymentStatus, transaction_id: Optional[str] = None, payment_details: Optional[Dict[str, Any]] = None
    ) -> Payment:
        """
        更新支付状态和可选的交易ID及其他详情。
        payment_details can include 'paid_at', 'notes', etc.
        """
        update_data: Dict[str, Any] = {"status": status}
        if transaction_id:
            update_data["transaction_id"] = transaction_id
        
        if status == PaymentStatus.SUCCESSFUL and "paid_at" not in (payment_details or {}):
            update_data["paid_at"] = datetime.utcnow()
        elif status == PaymentStatus.REFUNDED and "refunded_at" not in (payment_details or {}):
            update_data["refunded_at"] = datetime.utcnow()

        if payment_details:
            update_data.update(payment_details)
            
        return super().update(db, db_obj=db_obj, obj_in=update_data)

payment = CRUDPayment(Payment)
