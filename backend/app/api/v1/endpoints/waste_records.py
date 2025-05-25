from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.order import Order
from app.models.waste_record import WasteRecord
from app.schemas.waste_record import WasteRecordCreate, WasteRecordUpdate, WasteRecordResponse
from app.crud import crud_waste_record, crud_order, crud_transport_manager, crud_recycling_manager

router = APIRouter()

# Helper function to check if user can access/modify waste records for an order
async def check_order_waste_record_permission(db: Session, order_id: int, current_user: User) -> Order:
    order = crud_order.order.get(db, id=order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    can_access = False
    if current_user.is_superuser:
        can_access = True
    elif current_user.role == UserRole.TRANSPORT:
        # Dispatcher or Primary Manager of the order's transport company
        if order.transport_company_id:
            assoc = crud_transport_manager.transport_manager.get_by_company_and_manager_user(
                db, transport_company_id=order.transport_company_id, manager_user_id=current_user.id
            )
            if assoc and (assoc.is_primary or assoc.role == "DISPATCHER"): # Assuming TransportRole.DISPATCHER string value
                can_access = True
        # Assigned driver for the order
        if order.driver_assoc_id and order.driver_association and order.driver_association.manager_id == current_user.id:
            can_access = True
    elif current_user.role == UserRole.RECYCLING:
        # Manager (any role) of the order's recycling company
        if order.recycling_company_id:
            assoc = crud_recycling_manager.recycling_manager.get_by_company_and_manager_user(
                db, recycling_company_id=order.recycling_company_id, manager_user_id=current_user.id
            )
            if assoc:
                can_access = True
    
    if not can_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to manage waste records for this order."
        )
    return order


@router.post("/", response_model=WasteRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_waste_record(
    *,
    db: Session = Depends(get_db),
    record_in: WasteRecordCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create a new waste record for an order.
    Typically created by transport or recycling personnel.
    """
    await check_order_waste_record_permission(db, record_in.order_id, current_user)
    
    record = crud_waste_record.waste_record.create_with_order_and_user(
        db, obj_in=record_in, order_id=record_in.order_id, user_id=current_user.id
    )
    # Eager load user for response
    reloaded_record = crud_waste_record.waste_record.get_with_user(db, id=record.id)
    return WasteRecordResponse.model_validate(reloaded_record).model_dump() if reloaded_record else None # Return None or raise error if not found


@router.get("/order/{order_id}", response_model=List[WasteRecordResponse])
async def list_waste_records_for_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    List all waste records associated with a specific order.
    """
    await check_order_waste_record_permission(db, order_id, current_user)
    records = crud_waste_record.waste_record.get_by_order_id(db, order_id=order_id)
    return records


@router.get("/{record_id}", response_model=WasteRecordResponse)
async def read_waste_record(
    *,
    db: Session = Depends(get_db),
    record_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get a specific waste record by its ID.
    """
    record = crud_waste_record.waste_record.get_with_user(db, id=record_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Waste record not found")
    
    await check_order_waste_record_permission(db, record.order_id, current_user)
    return WasteRecordResponse.model_validate(record).model_dump()


@router.put("/{record_id}", response_model=WasteRecordResponse)
async def update_waste_record(
    *,
    db: Session = Depends(get_db),
    record_id: int,
    record_in: WasteRecordUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update an existing waste record.
    """
    db_record = crud_waste_record.waste_record.get(db, id=record_id)
    if not db_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Waste record not found")

    await check_order_waste_record_permission(db, db_record.order_id, current_user)
    
    # Update recorded_by_user_id if the updater is different and it's being explicitly passed or if we decide to track last modifier
    update_data = record_in.model_validate().model_dump()
    if 'recorded_by_user_id' not in update_data or update_data.get('recorded_by_user_id') != current_user.id :
         # This field might be for original recorder. Or we can add a last_modified_by_user_id
         # For now, let's assume record_in can update it if provided by an authorized user.
         # If we want to enforce that only the creator or superuser can change `recorded_by_user_id`, add logic here.
         pass


    updated_record_db = crud_waste_record.waste_record.update(db, db_obj=db_record, obj_in=update_data)
    reloaded_updated_record = crud_waste_record.waste_record.get_with_user(db, id=updated_record_db.id)
    return WasteRecordResponse.model_validate(reloaded_updated_record).model_dump() if reloaded_updated_record else None # Re-fetch with user for response


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_waste_record(
    *,
    db: Session = Depends(get_db),
    record_id: int,
    current_user: User = Depends(get_current_active_user)
) -> None:
    """
    Delete a waste record.
    Only superusers or potentially the user who created it (if allowed by business logic).
    """
    db_record = crud_waste_record.waste_record.get(db, id=record_id)
    if not db_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Waste record not found")

    # More restrictive delete: only superuser or manager of the company related to the order phase
    await check_order_waste_record_permission(db, db_record.order_id, current_user)
    
    # Add more specific delete permission if needed (e.g., only creator or superuser)
    # For now, if user has access to the order's waste records (checked above), they can delete.
    # This might be too permissive.
    # A stricter check:
    # if not current_user.is_superuser and db_record.recorded_by_user_id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this waste record")
    
    crud_waste_record.waste_record.remove(db, id=record_id)
    return
