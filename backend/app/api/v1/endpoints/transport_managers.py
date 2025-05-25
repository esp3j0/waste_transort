from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.transport_company import TransportCompany
from app.models.transport_manager import TransportManager, TransportRole, DriverStatus
from app.schemas.transport_manager import TransportManagerCreate, TransportManagerUpdate, TransportManagerResponse, DriverStatusUpdate
from app.crud import crud_transport_company, crud_transport_manager, crud_user

router = APIRouter()

# This router will be typically prefixed e.g. /transport-companies/{company_id}/managers or /transport-personnel
# For simplicity, using a flatter structure for now, but nested routing is common.

@router.post("/", response_model=TransportManagerResponse, status_code=status.HTTP_201_CREATED)
async def add_manager_to_transport_company(
    *,
    db: Session = Depends(get_db),
    manager_in: TransportManagerCreate, # Contains transport_company_id, manager_id (user_id), is_primary, role, driver details
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """将用户分配到运输公司，担任特定角色（主要管理员、调度员、司机）。"""
    company = crud_transport_company.transport_company.get(db, id=manager_in.transport_company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transport company {manager_in.transport_company_id} not found.")

    target_user = crud_user.user.get(db, id=manager_in.manager_id)
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {manager_in.manager_id} not found.")
    if target_user.role != UserRole.TRANSPORT and not target_user.is_superuser:
        # Allow superusers to be assigned for testing/setup? Generally, assignees should have TRANSPORT role.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User {target_user.username} must have TRANSPORT role to be assigned.")

    # Permissions: Superuser or primary manager of the target company can add personnel
    can_add_personnel = False
    if current_user.is_superuser:
        can_add_personnel = True
    else:
        current_user_assoc = crud_transport_manager.transport_manager.get_by_company_and_manager_user(
            db, transport_company_id=manager_in.transport_company_id, manager_user_id=current_user.id
        )
        if current_user_assoc and current_user_assoc.is_primary:
            can_add_personnel = True
    
    if not can_add_personnel:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add personnel to this company.")

    try:
        manager_assoc = crud_transport_manager.transport_manager.create_manager_for_company(db, obj_in=manager_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return TransportManagerResponse.model_validate(manager_assoc).model_dump()

@router.get("/company/{company_id}", response_model=List[TransportManagerResponse])
async def list_managers_for_company(
    *,
    db: Session = Depends(get_db),
    company_id: int,
    role_filter: Optional[TransportRole] = None,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取指定运输公司的管理人员列表 (可按角色过滤)。"""
    company = crud_transport_company.transport_company.get(db, id=company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transport company {company_id} not found.")
    
    # Permissions: Superuser or any manager of this company can view personnel list
    can_view_list = False
    if current_user.is_superuser:
        can_view_list = True
    else:
        assoc = crud_transport_manager.transport_manager.get_by_company_and_manager_user(
            db, transport_company_id=company_id, manager_user_id=current_user.id
        )
        if assoc: # If current user is associated with the company in any manager role
            can_view_list = True
    if not can_view_list:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view personnel for this company.")

    if role_filter == TransportRole.DRIVER:
        personnel = crud_transport_manager.transport_manager.get_drivers_by_company(db, transport_company_id=company_id)
    elif role_filter == TransportRole.DISPATCHER:
        personnel = crud_transport_manager.transport_manager.get_dispatchers_by_company(db, transport_company_id=company_id)
    else:
        personnel = crud_transport_manager.transport_manager.get_managers_by_company(db, transport_company_id=company_id)
    
    if role_filter:
        personnel = [p for p in personnel if p.role == role_filter.value]
    
    return [TransportManagerResponse.model_validate(p).model_dump() for p in personnel]

@router.get("/{assoc_id}", response_model=TransportManagerResponse)
async def get_transport_manager_association(
    *,
    db: Session = Depends(get_db),
    assoc_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取特定的运输管理人员关联详情。"""
    # TransportManagerResponse often includes nested User info. CRUD needs get_with_user_details or similar.
    assoc = crud_transport_manager.transport_manager.get_with_user_details(db, id=assoc_id) # Assumed method
    if not assoc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transport manager association not found.")
    
    # Permissions: Superuser, the user themselves, or primary manager of their company
    can_view = False
    if current_user.is_superuser or assoc.manager_id == current_user.id:
        can_view = True
    else:
        primary_assoc = crud_transport_manager.transport_manager.get_by_company_and_manager_user(
            db, transport_company_id=assoc.transport_company_id, manager_user_id=current_user.id
        )
        if primary_assoc and primary_assoc.is_primary:
            can_view = True
    if not can_view:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this manager association.")
    return TransportManagerResponse.model_validate(assoc).model_dump()

@router.put("/{assoc_id}", response_model=TransportManagerResponse)
async def update_transport_manager_association(
    *,
    db: Session = Depends(get_db),
    assoc_id: int,
    manager_in: TransportManagerUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """更新运输管理人员的关联信息（角色、是否主要管理员）。"""
    db_assoc = crud_transport_manager.transport_manager.get(db, id=assoc_id)
    if not db_assoc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transport manager association not found.")

    # Permissions: Superuser, or primary manager of the company.
    # Target user cannot change their own is_primary status unless they are already primary and making someone else primary.
    can_update = False
    acting_user_is_primary = False
    if not current_user.is_superuser:
        current_user_assoc = crud_transport_manager.transport_manager.get_by_company_and_manager_user(
            db, transport_company_id=db_assoc.transport_company_id, manager_user_id=current_user.id
        )
        if current_user_assoc and current_user_assoc.is_primary:
            acting_user_is_primary = True
    
    if current_user.is_superuser or acting_user_is_primary:
        can_update = True
    
    if not can_update:
        # Allow user to update their own non-primary, non-role fields (e.g. driver_license_number if they are a driver)
        if db_assoc.manager_id == current_user.id and manager_in.is_primary is None and manager_in.role is None:
            pass # Allow self-update of own details like license if driver
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this manager association.")

    # Business logic for primary manager changes / role changes (some handled in CRUD)
    if manager_in.is_primary is True and not db_assoc.is_primary: # Promoting to primary
        if not (current_user.is_superuser or acting_user_is_primary):
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only superuser or company's primary manager can promote to primary.")
    
    # Prevent a primary manager from unsetting themselves as primary if they are the only one
    if db_assoc.is_primary and manager_in.is_primary is False:
        other_primaries = db.query(TransportManager).filter(
            TransportManager.transport_company_id == db_assoc.transport_company_id,
            TransportManager.is_primary == True,
            TransportManager.id != db_assoc.id
        ).count()
        if other_primaries == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove the only primary manager. Assign another primary manager first.")

    try:
        updated_assoc_db = crud_transport_manager.transport_manager.update(
            db, db_obj=db_assoc, obj_in=manager_in, current_user_id=current_user.id # Pass current_user if CRUD needs it
        )
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    reloaded_assoc = crud_transport_manager.transport_manager.get_with_user_details(db, id=updated_assoc_db.id) # Assumed method
    return TransportManagerResponse.model_validate(reloaded_assoc).model_dump() if reloaded_assoc else None

@router.put("/drivers/{driver_assoc_id}/status", response_model=TransportManagerResponse)
async def update_driver_status_by_association(
    *,
    db: Session = Depends(get_db),
    driver_assoc_id: int, # This is TransportManager.id for a driver
    status_in: DriverStatusUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """通过管理关联ID更新司机状态。"""
    driver_assoc = crud_transport_manager.transport_manager.get(db, id=driver_assoc_id)
    if not driver_assoc or driver_assoc.role != TransportRole.DRIVER:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver association not found or not a driver.")

    # Permissions: Superuser, primary manager of the driver's company, or a dispatcher of the same company.
    can_update_status = False
    if current_user.is_superuser:
        can_update_status = True
    else:
        actor_assoc = crud_transport_manager.transport_manager.get_by_company_and_manager_user(
            db, transport_company_id=driver_assoc.transport_company_id, manager_user_id=current_user.id
        )
        if actor_assoc and (actor_assoc.is_primary or actor_assoc.role == TransportRole.DISPATCHER):
            can_update_status = True
    
    if not can_update_status:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this driver's status.")

    updated_assoc_db = crud_transport_manager.transport_manager.update(db, db_obj=driver_assoc, obj_in=status_in)
    reloaded_assoc = crud_transport_manager.transport_manager.get_with_user_details(db, id=updated_assoc_db.id) # Assumed
    return TransportManagerResponse.model_validate(reloaded_assoc).model_dump() if reloaded_assoc else None

@router.delete("/{assoc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_manager_from_transport_company(
    *,
    db: Session = Depends(get_db),
    assoc_id: int, # TransportManager.id
    current_user: User = Depends(get_current_active_user)
) -> None:
    """从运输公司移除管理人员 (解除关联)。"""
    db_assoc = crud_transport_manager.transport_manager.get(db, id=assoc_id)
    if not db_assoc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transport manager association not found.")

    # Permissions: Superuser or primary manager of the company.
    # User cannot remove themselves this way (especially if primary).
    if db_assoc.manager_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot remove yourself using this endpoint.")

    can_remove = False
    if current_user.is_superuser:
        can_remove = True
    else:
        actor_assoc = crud_transport_manager.transport_manager.get_by_company_and_manager_user(
            db, transport_company_id=db_assoc.transport_company_id, manager_user_id=current_user.id
        )
        if actor_assoc and actor_assoc.is_primary:
            can_remove = True
    
    if not can_remove:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to remove this manager association.")
    
    if db_assoc.is_primary:
        other_primaries = db.query(TransportManager).filter(
            TransportManager.transport_company_id == db_assoc.transport_company_id,
            TransportManager.is_primary == True,
            TransportManager.id != db_assoc.id
        ).count()
        if other_primaries == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove the only primary manager. Assign another primary manager first or delete the company.")

    crud_transport_manager.transport_manager.remove(db, id=assoc_id)
    return 