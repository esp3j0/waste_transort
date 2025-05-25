from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

# 从模型导入枚举，以便在 schema 中使用和校验
from app.models.payment import PaymentMethod as PaymentMethodEnum
from app.models.payment import PaymentStatus as PaymentStatusEnum


class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    ALIPAY = "alipay"
    WECHAT_PAY = "wechat_pay"
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"

# 支付记录基础模型
class PaymentBase(BaseModel):
    amount: float = Field(..., gt=0, description="支付金额")
    currency: str = Field("CNY", description="货币单位")
    payment_method: Optional[PaymentMethod] = Field(None, description="支付方式")
    payment_gateway: Optional[str] = Field(None, description="支付网关")
    notes: Optional[str] = Field(None, description="支付备注")

# 创建支付记录模型
class PaymentCreate(PaymentBase):
    order_id: int = Field(..., description="关联的订单ID")
    # status is PENDING by default in model
    # transaction_id might be set after creation or during update by gateway callback

# 更新支付记录模型 (主要用于更新状态、交易ID等)
class PaymentUpdate(BaseModel):
    payment_method: Optional[PaymentMethod] = Field(None, description="支付方式")
    transaction_id: Optional[str] = Field(None, description="支付网关交易ID")
    status: Optional[PaymentStatus] = Field(None, description="支付状态")
    paid_at: Optional[datetime] = Field(None, description="支付成功时间")
    refunded_at: Optional[datetime] = Field(None, description="退款时间")
    notes: Optional[str] = Field(None, description="支付备注")

# 支付记录响应模型
class PaymentResponse(PaymentBase):
    id: int = Field(..., description="支付记录ID")
    order_id: int = Field(..., description="关联的订单ID")
    status: PaymentStatus = Field(..., description="支付状态")
    transaction_id: Optional[str] = Field(None, description="支付网关交易ID")
    initiated_at: datetime = Field(..., description="支付发起时间")
    paid_at: Optional[datetime] = Field(None, description="支付成功时间")
    refunded_at: Optional[datetime] = Field(None, description="退款时间")
    
    class Config:
        from_attributes = True
