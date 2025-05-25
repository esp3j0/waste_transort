from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.recycling_company import RecyclingCompany
from app.models.recycling_manager import RecyclingManager, RecyclingRole
from app.schemas.recycling_manager import RecyclingManagerCreate, RecyclingManagerUpdate, RecyclingManagerResponse
from app.crud import crud_recycling_company, crud_recycling_manager, crud_user

router = APIRouter()

@router.post("/", response_model=RecyclingManagerResponse, status_code=status.HTTP_201_CREATED)
async def add_manager_to_recycling_company(
    *,
    db: Session = Depends(get_db),
    manager_in: RecyclingManagerCreate, # Contains recycling_company_id, manager_id, is_primary, role
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """将用户分配到回收公司，担任特定角色。"""
    company = crud_recycling_company.recycling_company.get(db, id=manager_in.recycling_company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Recycling company {manager_in.recycling_company_id} not found.")

    target_user = crud_user.user.get(db, id=manager_in.manager_id)
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {manager_in.manager_id} not found.")
    if target_user.role != UserRole.RECYCLING and not target_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User {target_user.username} must have RECYCLING role to be assigned.")

    can_add_personnel = False
    if current_user.is_superuser:
        can_add_personnel = True
    else:
        current_user_assoc = crud_recycling_manager.recycling_manager.get_by_company_and_manager_user(
            db, recycling_company_id=manager_in.recycling_company_id, manager_user_id=current_user.id
        )
        if current_user_assoc and current_user_assoc.is_primary:
            can_add_personnel = True
    
    if not can_add_personnel:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add personnel to this company.")

    try:
        manager_assoc = crud_recycling_manager.recycling_manager.create_manager_for_company(db, obj_in=manager_in)
    except HTTPException as e: # CRUD might raise HTTPException directly now
        raise e
    except ValueError as e: # Catch other ValueErrors from CRUD if any
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return RecyclingManagerResponse.model_validate(manager_assoc).model_dump()

@router.get("/company/{company_id}", response_model=List[RecyclingManagerResponse])
async def list_managers_for_recycling_company(
    *,
    db: Session = Depends(get_db),
    company_id: int,
    role_filter: Optional[RecyclingRole] = None,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取指定回收公司的管理人员列表。"""
    company = crud_recycling_company.recycling_company.get(db, id=company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Recycling company {company_id} not found.")
    
    can_view_list = False
    if current_user.is_superuser:
        can_view_list = True
    else:
        assoc = crud_recycling_manager.recycling_manager.get_by_company_and_manager_user(
            db, recycling_company_id=company_id, manager_user_id=current_user.id
        )
        if assoc: # Any manager of the company can view the list
            can_view_list = True
    if not can_view_list:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view personnel for this company.")

    personnel = crud_recycling_manager.recycling_manager.get_managers_by_company(db, recycling_company_id=company_id)
    if role_filter:
        personnel = [p for p in personnel if p.role == role_filter]
    return [RecyclingManagerResponse.model_validate(p).model_dump() for p in personnel]

@router.get("/{manager_assoc_id}", response_model=RecyclingManagerResponse)
async def get_recycling_manager_association_details(
    *,
    db: Session = Depends(get_db),
    manager_assoc_id: int, 
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取特定的回收管理人员关联详情。"""
    assoc = crud_recycling_manager.recycling_manager.get(db, id=manager_assoc_id) # Use basic get
    if not assoc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recycling manager association not found.")
    
    can_view = False
    if current_user.is_superuser or assoc.manager_id == current_user.id:
        can_view = True
    else:
        primary_for_company = crud_recycling_manager.recycling_manager.get_primary_manager_for_company(
            db, property_company_id=assoc.recycling_company_id # Corrected to recycling_company_id
        )
        if primary_for_company and primary_for_company.manager_id == current_user.id:
            can_view = True
    if not can_view:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this manager association.")
    return RecyclingManagerResponse.model_validate(assoc).model_dump()

@router.put("/{manager_assoc_id}", response_model=RecyclingManagerResponse)
async def update_recycling_manager_association(
    *,
    db: Session = Depends(get_db),
    manager_assoc_id: int, 
    update_in: RecyclingManagerUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """更新回收管理人员的关联信息。"""
    db_assoc = crud_recycling_manager.recycling_manager.get(db, id=manager_assoc_id)
    if not db_assoc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recycling manager association not found.")

    can_update = False
    acting_user_is_primary_of_company = False
    if not current_user.is_superuser:
        current_user_company_assoc = crud_recycling_manager.recycling_manager.get_by_company_and_manager_user(
            db, recycling_company_id=db_assoc.recycling_company_id, manager_user_id=current_user.id
        )
        if current_user_company_assoc and current_user_company_assoc.is_primary:
            acting_user_is_primary_of_company = True
    
    if current_user.is_superuser or acting_user_is_primary_of_company:
        can_update = True
    
    # User cannot update their own primary status directly unless they are superuser or primary manager themselves
    if db_assoc.manager_id == current_user.id and not can_update: # User is trying to update self
        if update_in.is_primary is not None and update_in.is_primary != db_assoc.is_primary:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot change your own primary status.")
        # Allow role update for self if not changing primary status by this action
        if update_in.is_primary is None: # Only allow role update
            can_update = True 

    if not can_update:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this manager association.")

    # Prevent a primary manager from unsetting themselves as primary if they are the only one
    if db_assoc.is_primary and update_in.is_primary is False:
        other_primary_managers = crud_recycling_manager.recycling_manager.get_primary_manager_for_company(
            db, property_company_id=db_assoc.recycling_company_id, exclude_self_id=db_assoc.id # Corrected to recycling_company_id
        )
        if not other_primary_managers:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove the only primary manager. Assign another primary manager first.")

    try:
        updated_assoc = crud_recycling_manager.recycling_manager.update(db, db_obj=db_assoc, obj_in=update_in)
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    return RecyclingManagerResponse.model_validate(updated_assoc).model_dump()

@router.delete("/{manager_assoc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_manager_from_recycling_company(
    *,
    db: Session = Depends(get_db),
    manager_assoc_id: int, # RecyclingManager.id
    current_user: User = Depends(get_current_active_user)
) -> None:
    """从回收公司移除管理人员 (解除关联)。"""
    db_assoc = crud_recycling_manager.recycling_manager.get(db, id=manager_assoc_id)
    if not db_assoc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recycling manager association not found.")

    if db_assoc.manager_id == current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot remove yourself. Contact a primary manager or superuser.")

    can_remove = False
    if current_user.is_superuser:
        can_remove = True
    else:
        actor_assoc = crud_recycling_manager.recycling_manager.get_by_company_and_manager_user(
            db, recycling_company_id=db_assoc.recycling_company_id, manager_user_id=current_user.id
        )
        if actor_assoc and actor_assoc.is_primary:
            can_remove = True
    
    if not can_remove:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to remove this manager association.")
    
    if db_assoc.is_primary:
        other_primary_managers = crud_recycling_manager.recycling_manager.get_primary_manager_for_company(
             db, property_company_id=db_assoc.recycling_company_id, exclude_self_id=db_assoc.id # Corrected to recycling_company_id
        )
        if not other_primary_managers:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove the only primary manager. Assign another primary manager first or delete the company.")

    crud_recycling_manager.recycling_manager.remove(db, id=manager_assoc_id)
    return 