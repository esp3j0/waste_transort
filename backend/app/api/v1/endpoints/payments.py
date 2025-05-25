from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.deps import get_current_active_user # For user initiating payment
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.order import Order, OrderStatus
from app.models.payment import Payment, PaymentStatus as PaymentStatusEnum, PaymentMethod as PaymentMethodEnum
from app.schemas.payment import PaymentCreate, PaymentUpdate, PaymentResponse, PaymentStatus, PaymentMethod
from app.crud import crud_payment, crud_order

router = APIRouter()

# Helper to check order access for payment operations
async def check_order_payment_permission(db: Session, order_id: int, current_user: User, allow_customer: bool = True) -> Order:
    order = crud_order.order.get(db, id=order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    can_access = False
    if current_user.is_superuser:
        can_access = True
    elif allow_customer and order.customer_id == current_user.id: # Customer can access their own order's payments
        can_access = True
    # Potentially add other roles if they can manage payments (e.g., finance admin)
    # For now, superuser or customer (if applicable for the operation)

    if not can_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to manage payments for this order."
        )
    return order

@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def initiate_payment_for_order(
    *,
    db: Session = Depends(get_db),
    payment_in: PaymentCreate, # order_id should be in here
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Initiate a payment record for an order.
    Typically called by the customer or system when payment is required.
    Order price should already be set on the order object.
    """
    order = await check_order_payment_permission(db, payment_in.order_id, current_user, allow_customer=True)

    if order.price <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order price must be set and positive to initiate payment.")
    
    # Check if amount matches order.price (or handle partial payments if supported)
    if payment_in.amount != order.price:
        # This logic could be more complex if partial payments or different amounts are allowed
        # For now, assume payment_in.amount should match order.price
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail=f"Payment amount {payment_in.amount} does not match order price {order.price}.")

    # Check for existing PENDING or SUCCESSFUL payments for this order to avoid duplicates
    existing_payments = crud_payment.payment.get_by_order_id(db, order_id=order.id)
    for ep in existing_payments:
        if ep.status == PaymentStatusEnum.SUCCESSFUL:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order has already been successfully paid.")
        # Allow creating a new PENDING payment if previous attempts failed or were cancelled
        # but maybe not if one is already PENDING and not expired.
        # For simplicity now, we'll allow creating a new one.

    payment = crud_payment.payment.create_for_order(db, obj_in=payment_in, order_id=order.id)
    
    # Update order's payment_status field
    if order.payment_status != payment_in.status.value: # if schema status is different from model
         crud_order.order.update(db, db_obj=order, obj_in={"payment_status": PaymentStatusEnum.PENDING.value})


    return PaymentResponse.model_validate(payment).model_dump()

@router.get("/order/{order_id}", response_model=List[PaymentResponse])
async def list_payments_for_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """List all payment records associated with a specific order."""
    await check_order_payment_permission(db, order_id, current_user, allow_customer=True)
    payments = crud_payment.payment.get_by_order_id(db, order_id=order_id)
    return [PaymentResponse.model_validate(payment).model_dump() for payment in payments]

@router.get("/{payment_id}", response_model=PaymentResponse)
async def read_payment(
    *,
    db: Session = Depends(get_db),
    payment_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get a specific payment record by its ID."""
    payment = crud_payment.payment.get(db, id=payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment record not found")
    
    await check_order_payment_permission(db, payment.order_id, current_user, allow_customer=True)
    return PaymentResponse.model_validate(payment).model_dump()

# This is a simulated callback endpoint from a payment gateway
@router.post("/callback/{payment_id}/gateway", response_model=PaymentResponse)
async def payment_gateway_callback(
    *,
    db: Session = Depends(get_db),
    payment_id: int,
    # In a real scenario, this would be an unauthenticated endpoint,
    # and the payload would be validated using a signature from the gateway.
    # For simulation, we'll just pass data.
    transaction_id: str = Body(...),
    gateway_status: str = Body(..., description="Status from gateway, e.g., 'success', 'failed'"),
    # current_user: User = Depends(get_current_active_user) # Not used for actual gateway callback
) -> Any:
    """
    Simulated payment gateway callback to update payment status.
    NOTE: This endpoint would need proper security (e.g., signature validation) in a real system.
    """
    payment = crud_payment.payment.get(db, id=payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment record not found for callback")

    order = crud_order.order.get(db, id=payment.order_id)
    if not order:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order associated with payment not found")


    new_status: Optional[PaymentStatusEnum] = None
    if gateway_status.lower() == "success":
        new_status = PaymentStatusEnum.SUCCESSFUL
    elif gateway_status.lower() == "failed":
        new_status = PaymentStatusEnum.FAILED
    else:
        # Handle other statuses or log as unknown
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown gateway status")

    if new_status:
        payment_details = {}
        if new_status == PaymentStatusEnum.SUCCESSFUL:
            payment_details["paid_at"] = datetime.utcnow()
            # Update order payment status and potentially overall order status
            crud_order.order.update(db, db_obj=order, obj_in={"payment_status": new_status.value, "payment_time": datetime.utcnow()})
            # Example: if order was PENDING_PAYMENT, move to PENDING or PROPERTY_CONFIRMED etc.
            # This depends on specific order workflow after payment.
            # For now, just updating payment_status on order.
        
        elif new_status == PaymentStatusEnum.FAILED:
             crud_order.order.update(db, db_obj=order, obj_in={"payment_status": new_status.value})


        updated_payment = crud_payment.payment.update_payment_status(
            db, db_obj=payment, status=new_status, transaction_id=transaction_id, payment_details=payment_details
        )
        return PaymentResponse.model_validate(updated_payment).model_dump()
    
    return PaymentResponse.model_validate(payment).model_dump() # Should not be reached if status is handled


# Admin/Superuser endpoint to manually update payment status (e.g., for bank transfers)
@router.put("/{payment_id}/status", response_model=PaymentResponse)
async def manually_update_payment_status(
    *,
    db: Session = Depends(get_db),
    payment_id: int,
    status_update: PaymentUpdate, # Use PaymentUpdate schema, which includes status
    current_user: User = Depends(get_current_active_user)
):
    """Manually update payment status (for admins/superusers or specific roles)."""
    if not current_user.is_superuser: # Restrict to superuser for now
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to manually update payment status.")

    payment = crud_payment.payment.get(db, id=payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment record not found")

    order = crud_order.order.get(db, id=payment.order_id)
    if not order:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order associated with payment not found")

    update_data = status_update.model_dump(exclude_unset=True)
    
    # If status is being updated, especially to SUCCESSFUL or REFUNDED, set relevant timestamps
    new_status_val = update_data.get("status")
    if new_status_val:
        try:
            new_status_enum = PaymentStatusEnum(new_status_val) # Validate if string is valid enum
            if new_status_enum == PaymentStatusEnum.SUCCESSFUL and "paid_at" not in update_data:
                update_data["paid_at"] = datetime.utcnow()
                crud_order.order.update(db, db_obj=order, obj_in={"payment_status": new_status_enum.value, "payment_time": datetime.utcnow()})
            elif new_status_enum == PaymentStatusEnum.REFUNDED and "refunded_at" not in update_data:
                update_data["refunded_at"] = datetime.utcnow()
                crud_order.order.update(db, db_obj=order, obj_in={"payment_status": new_status_enum.value}) # Could also clear payment_time
            else: # For other statuses like PENDING, FAILED, CANCELLED
                crud_order.order.update(db, db_obj=order, obj_in={"payment_status": new_status_enum.value})

        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid payment status: {new_status_val}")


    updated_payment = crud_payment.payment.update(db, db_obj=payment, obj_in=update_data)
    return PaymentResponse.model_validate(updated_payment).model_dump()
