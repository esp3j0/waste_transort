from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.transport_company import TransportCompany
from app.schemas.transport_company import TransportCompanyCreate, TransportCompanyUpdate, TransportCompanyResponse
from app.schemas.transport_manager import TransportManagerCreate, TransportManagerResponse # For adding managers
from app.crud import crud_transport_company, crud_transport_manager, crud_user # crud_user for checking if user exists

router = APIRouter()

@router.post("/", response_model=TransportCompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_transport_company(
    *,
    db: Session = Depends(get_db),
    company_in: TransportCompanyCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """创建新的运输公司。"""
    if not current_user.is_superuser and current_user.role != UserRole.TRANSPORT:
        # Allow users with TRANSPORT role to create their own company if they are not yet part of one?
        # Or restrict to superuser only for initial company creation.
        # For now, let's assume a TRANSPORT role user can create ONE company and becomes its primary manager.
        pass # Add more specific logic here if needed.

    existing_company = crud_transport_company.transport_company.get_by_name(db, name=company_in.name)
    if existing_company:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Transport company '{company_in.name}' already exists.")

    company = crud_transport_company.transport_company.create_with_primary_manager(
        db=db, obj_in=company_in, primary_manager_user_id=current_user.id
    )
    return TransportCompanyResponse.model_validate(company).model_dump()

@router.get("/", response_model=List[TransportCompanyResponse])
async def read_transport_companies(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user) # Permissions?
) -> Any:
    """获取运输公司列表。"""
    # Only superusers or users with TRANSPORT role can list companies.
    # Transport role users might see only their associated companies or all, depending on refined logic.
    if not current_user.is_superuser and current_user.role != UserRole.TRANSPORT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to list transport companies.")

    if current_user.is_superuser:
        companies = crud_transport_company.transport_company.get_multi(db, skip=skip, limit=limit)
    else: # UserRole.TRANSPORT
        # Default: show companies they are associated with. Could be refined.
        companies = crud_transport_company.transport_company.get_by_manager_user(
            db, manager_user_id=current_user.id, skip=skip, limit=limit
        )
    return [TransportCompanyResponse.model_validate(c).model_dump() for c in companies]

@router.get("/{company_id}", response_model=TransportCompanyResponse)
async def read_transport_company(
    *,
    db: Session = Depends(get_db),
    company_id: int,
    current_user: User = Depends(get_current_active_user) # Permissions?
) -> Any:
    """获取指定运输公司信息。"""
    # Similar to RecyclingCompany, fetch with managers/vehicles if response schema needs them.
    # Assuming TransportCompanyResponse is flat or handles this via ORM for now.
    company = crud_transport_company.transport_company.get_with_details(db, id=company_id) # Assumed method
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transport company not found.")
    
    # ... (permission check) ...
    return TransportCompanyResponse.model_validate(company).model_dump()

@router.put("/{company_id}", response_model=TransportCompanyResponse)
async def update_transport_company(
    *,
    db: Session = Depends(get_db),
    company_id: int,
    company_in: TransportCompanyUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """更新运输公司信息。"""
    company = crud_transport_company.transport_company.get(db, id=company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transport company not found.")
    
    # ... (permission check and name uniqueness) ...
            
    updated_company_db = crud_transport_company.transport_company.update(db, db_obj=company, obj_in=company_in)
    # Re-fetch with details for full response
    full_updated_company = crud_transport_company.transport_company.get_with_details(db, id=updated_company_db.id) # Assumed method
    return TransportCompanyResponse.model_validate(full_updated_company).model_dump() if full_updated_company else None

@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transport_company(
    *,
    db: Session = Depends(get_db),
    company_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """删除运输公司。"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only superusers can delete transport companies.")

    company = crud_transport_company.transport_company.get(db, id=company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transport company not found.")

    # Consider what happens to orders, managers, vehicles associated. Cascade delete set on models?
    deleted_company = crud_transport_company.transport_company.remove(db, id=company_id)
    return deleted_company

# Endpoints for managing managers (drivers, dispatchers) within a company will be in transport_managers.py (or here if preferred)
# For now, keeping company-specific personnel management separate for clarity, similar to properties.py vs property_managers.py logic. 