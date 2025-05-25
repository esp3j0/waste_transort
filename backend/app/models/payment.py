from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base_class import Base

class PaymentMethod(str, enum.Enum):
    CREDIT_CARD = "credit_card"
    ALIPAY = "alipay"
    WECHAT_PAY = "wechat_pay"
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash" # 可能在某些场景下使用

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"       # 待支付
    PROCESSING = "processing" # 处理中
    SUCCESSFUL = "successful" # 支付成功
    FAILED = "failed"         # 支付失败
    REFUNDED = "refunded"     # 已退款
    CANCELLED = "cancelled"   # 已取消

class Payment(Base):
    """支付记录模型"""
    __tablename__ = "payment"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("order.id"), nullable=False, index=True)
    
    amount = Column(Float, nullable=False, comment="支付金额")
    currency = Column(String, default="CNY", nullable=False, comment="货币单位")
    
    payment_method = Column(SAEnum(PaymentMethod, name="payment_method_enum", create_type=False), nullable=True, comment="支付方式")
    payment_gateway = Column(String, nullable=True, comment="支付网关，如：stripe, alipay_sdk")
    transaction_id = Column(String, nullable=True, unique=True, index=True, comment="支付网关交易ID")
    
    status = Column(SAEnum(PaymentStatus, name="payment_status_enum", create_type=False), default=PaymentStatus.PENDING, nullable=False, comment="支付状态")
    
    initiated_at = Column(DateTime, default=datetime.utcnow, comment="支付发起时间")
    paid_at = Column(DateTime, nullable=True, comment="支付成功时间")
    refunded_at = Column(DateTime, nullable=True, comment="退款时间")
    
    notes = Column(String, nullable=True, comment="支付备注")
    
    # 关系
    order = relationship("Order", back_populates="payments")

    def __repr__(self):
        return f"<Payment(id={self.id}, order_id={self.order_id}, amount={self.amount}, status='{self.status}')>"
