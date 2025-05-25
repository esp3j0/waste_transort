from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.property_company import PropertyCompany
from app.models.property_manager import PropertyManager
# Enums for PropertyManager roles would go in models/property_manager.py if defined
# from app.models.property_manager import PropertyManagerRole # Example
from app.schemas.property_manager import PropertyManagerCreate, PropertyManagerUpdate, PropertyManagerResponse
from app.crud import crud_property_company, crud_property_manager, crud_user

router = APIRouter()

@router.post("/", response_model=PropertyManagerResponse, status_code=status.HTTP_201_CREATED)
async def add_manager_to_property_company(
    *,
    db: Session = Depends(get_db),
    manager_in: PropertyManagerCreate, # Contains property_company_id, manager_id, is_primary, role, community_id
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """将用户分配到物业公司，担任特定角色（主要管理员、普通管理员等）。"""
    company = crud_property_company.property_company.get(db, id=manager_in.property_company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Property company {manager_in.property_company_id} not found.")

    target_user = crud_user.user.get(db, id=manager_in.manager_id)
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {manager_in.manager_id} not found.")
    if target_user.role != UserRole.PROPERTY and not target_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User {target_user.username} must have PROPERTY role to be assigned.")

    can_add_personnel = False
    if current_user.is_superuser:
        can_add_personnel = True
    else:
        current_user_assoc = crud_property_manager.property_manager.get_by_property_company_and_manager_user(
            db, property_company_id=manager_in.property_company_id, manager_user_id=current_user.id
        )
        if current_user_assoc and current_user_assoc.is_primary:
            can_add_personnel = True
    
    if not can_add_personnel:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add personnel to this company.")

    try:
        # The CRUD create method now expects property_company_id within manager_in
        manager_assoc = crud_property_manager.property_manager.create(db, obj_in=manager_in)
    except HTTPException as e: # CRUD might raise HTTPException directly now
        raise e
    except ValueError as e: # Catch other ValueErrors from CRUD if any
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return PropertyManagerResponse.model_validate(manager_assoc).model_dump()

@router.get("/company/{company_id}", response_model=List[PropertyManagerResponse])
async def list_managers_for_property_company(
    *,
    db: Session = Depends(get_db),
    company_id: int,
    # role_filter: Optional[PropertyManagerRole] = None, # Add if roles are defined and filterable
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取指定物业公司的管理人员列表。"""
    company = crud_property_company.property_company.get(db, id=company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Property company {company_id} not found.")
    
    can_view_list = False
    if current_user.is_superuser:
        can_view_list = True
    else:
        assoc = crud_property_manager.property_manager.get_by_property_company_and_manager_user(
            db, property_company_id=company_id, manager_user_id=current_user.id
        )
        if assoc:
            can_view_list = True
    if not can_view_list:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view personnel for this company.")

    # Add role filtering if implemented in CRUD
    # if role_filter:
    #     personnel = crud_property_manager.property_manager.get_by_company_and_role(db, property_company_id=company_id, role=role_filter)
    # else:
    personnel = crud_property_manager.property_manager.get_managers_by_company(db, property_company_id=company_id)
    # if role_filter:
    #     personnel = [p for p in personnel if p.role == role_filter]
    return [PropertyManagerResponse.model_validate(p).model_dump() for p in personnel]

@router.get("/{manager_assoc_id}", response_model=PropertyManagerResponse)
async def get_property_manager_association_details(
    *,
    db: Session = Depends(get_db),
    manager_assoc_id: int, # This is PropertyManager.id
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取特定的物业管理人员关联详情。"""
    assoc = crud_property_manager.property_manager.get_with_details(db, id=manager_assoc_id)
    if not assoc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property manager association not found.")
    
    # Permission: superuser, the manager themselves, or primary manager of the company
    can_view = False
    if current_user.is_superuser or assoc.manager_id == current_user.id:
        can_view = True
    else:
        primary_for_company = crud_property_manager.property_manager.get_primary_manager_for_company(
            db, property_company_id=assoc.property_company_id
        )
        if primary_for_company and primary_for_company.manager_id == current_user.id:
            can_view = True
    if not can_view:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this manager association.")
    return PropertyManagerResponse.model_validate(assoc).model_dump()

@router.put("/{manager_assoc_id}", response_model=PropertyManagerResponse)
async def update_property_manager_association(
    *,
    db: Session = Depends(get_db),
    manager_assoc_id: int, # PropertyManager.id
    update_in: PropertyManagerUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """更新物业管理人员的关联信息（角色、是否主要管理员、小区）。"""
    db_assoc = crud_property_manager.property_manager.get(db, id=manager_assoc_id)
    if not db_assoc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property manager association not found.")

    can_update = False
    acting_user_is_primary_of_company = False
    if not current_user.is_superuser:
        current_user_company_assoc = crud_property_manager.property_manager.get_by_property_company_and_manager_user(
            db, property_company_id=db_assoc.property_company_id, manager_user_id=current_user.id
        )
        if current_user_company_assoc and current_user_company_assoc.is_primary:
            acting_user_is_primary_of_company = True
    
    if current_user.is_superuser or acting_user_is_primary_of_company:
        can_update = True
    
    if db_assoc.manager_id == current_user.id and not can_update: # User is trying to update self
        if update_in.is_primary is not None and update_in.is_primary != db_assoc.is_primary:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot change your own primary status.")
        if update_in.is_primary is None: 
            can_update = True 

    if not can_update:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this manager association.")

    # Logic for primary manager changes / role changes (some handled in CRUD)
    # Prevent a primary manager from unsetting themselves as primary if they are the only one for the company
    if db_assoc.is_primary and update_in.is_primary is False:
        other_primary_managers = crud_property_manager.property_manager.get_primary_manager_for_company(
            db, property_company_id=db_assoc.property_company_id, exclude_self_id=db_assoc.id
        )
        if not other_primary_managers: # if no OTHER primary manager exists
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove the only primary manager. Assign another primary manager first.")

    try:
        updated_assoc = crud_property_manager.property_manager.update(db, db_obj=db_assoc, obj_in=update_in)
    except HTTPException as e: # CRUD might raise HTTPException
        raise e
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    reloaded_assoc = crud_property_manager.property_manager.get_with_details(db, id=updated_assoc.id)
    return PropertyManagerResponse.model_validate(reloaded_assoc).model_dump() if reloaded_assoc else None


@router.delete("/{manager_assoc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_manager_from_property_company(
    *,
    db: Session = Depends(get_db),
    manager_assoc_id: int, # PropertyManager.id
    current_user: User = Depends(get_current_active_user)
) -> None:
    """从物业公司移除管理人员 (解除关联)。"""
    db_assoc = crud_property_manager.property_manager.get(db, id=manager_assoc_id)
    if not db_assoc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property manager association not found.")

    if db_assoc.manager_id == current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot remove yourself using this endpoint. Contact a primary manager or superuser.")

    can_remove = False
    if current_user.is_superuser:
        can_remove = True
    else:
        actor_assoc = crud_property_manager.property_manager.get_by_property_company_and_manager_user(
            db, property_company_id=db_assoc.property_company_id, manager_user_id=current_user.id
        )
        if actor_assoc and actor_assoc.is_primary:
            can_remove = True
    
    if not can_remove:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to remove this manager association.")
    
    if db_assoc.is_primary:
        other_primary_managers = crud_property_manager.property_manager.get_primary_manager_for_company(
             db, property_company_id=db_assoc.property_company_id, exclude_self_id=db_assoc.id
        )
        if not other_primary_managers:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove the only primary manager. Assign another primary manager first or delete the company.")

    crud_property_manager.property_manager.remove(db, id=manager_assoc_id)
    return 