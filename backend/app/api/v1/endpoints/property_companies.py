from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.property_company import PropertyCompany
from app.schemas.property_company import PropertyCompanyCreate, PropertyCompanyUpdate, PropertyCompanyResponse
from app.schemas.property_manager import PropertyManagerCreate # For auto-assigning primary manager
from app.crud import crud_property_company, crud_property_manager, crud_user # crud_user for checking if user exists

router = APIRouter()

@router.post("/", response_model=PropertyCompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_property_company(
    *,
    db: Session = Depends(get_db),
    company_in: PropertyCompanyCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """创建新的物业公司。"""
    # 权限：超级管理员或具有 PROPERTY 角色的用户可以创建公司
    if not current_user.is_superuser and current_user.role != UserRole.PROPERTY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限执行此操作"
        )

    existing_company = crud_property_company.property_company.get_by_name(db, name=company_in.name) # Assuming get_by_name exists
    if existing_company:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Property company '{company_in.name}' already exists.")

    # 使用 crud_property_company 中的 create_with_primary_manager
    company = crud_property_company.property_company.create_with_primary_manager(
        db=db, obj_in=company_in, primary_manager_user_id=current_user.id
    )
    return PropertyCompanyResponse.model_validate(company).model_dump()

@router.get("/", response_model=List[PropertyCompanyResponse])
async def read_property_companies(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取物业公司列表。"""
    if current_user.is_superuser:
        companies = crud_property_company.property_company.get_multi(db, skip=skip, limit=limit)
    elif current_user.role == UserRole.PROPERTY:
        # 物业用户只能查看自己管理的物业公司
        companies = crud_property_company.property_company.get_by_manager_user(
            db, manager_user_id=current_user.id, skip=skip, limit=limit
        )
    else:
        # 其他角色（如客户）可以查看所有激活的物业公司 (如果需要)
        # companies = crud_property_company.property_company.get_multi_active(db, skip=skip, limit=limit)
        # For now, restrict to superuser and property role users for listing
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权查看物业公司列表")
    return [PropertyCompanyResponse.model_validate(c).model_dump() for c in companies]

@router.get("/{company_id}", response_model=PropertyCompanyResponse)
async def read_property_company(
    *,
    db: Session = Depends(get_db),
    company_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取指定物业公司信息。"""
    company = crud_property_company.property_company.get_with_managers_and_communities(db, id=company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property company not found.")
    
    # Basic permission: superuser or any manager of this company can view
    can_view = False
    if current_user.is_superuser:
        can_view = True
    else:
        manager_assoc = crud_property_manager.property_manager.get_by_property_company_and_manager_user(
            db, property_company_id=company_id, manager_user_id=current_user.id
        )
        if manager_assoc:
            can_view = True
    
    if not can_view:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this property company.")
    return PropertyCompanyResponse.model_validate(company).model_dump()

@router.put("/{company_id}", response_model=PropertyCompanyResponse)
async def update_property_company(
    *,
    db: Session = Depends(get_db),
    company_id: int,
    company_in: PropertyCompanyUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """更新物业公司信息。"""
    company = crud_property_company.property_company.get(db, id=company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property company not found.")
    
    # Permission: Superuser or primary manager of this company
    can_update = False
    if current_user.is_superuser:
        can_update = True
    else:
        primary_manager = crud_property_manager.property_manager.get_primary_manager_for_company(
            db, property_company_id=company_id
        )
        if primary_manager and primary_manager.manager_id == current_user.id:
            can_update = True
            
    if not can_update:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this property company.")
            
    updated_company = crud_property_company.property_company.update(db, db_obj=company, obj_in=company_in)
    # Re-fetch with relations for full response
    full_updated_company = crud_property_company.property_company.get_with_managers_and_communities(db, id=updated_company.id)
    return PropertyCompanyResponse.model_validate(full_updated_company).model_dump() if full_updated_company else None

@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_property_company(
    *,
    db: Session = Depends(get_db),
    company_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """删除物业公司。"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only superusers can delete property companies.")

    company = crud_property_company.property_company.get(db, id=company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property company not found.")

    # Consider cascade delete implications (managers, communities)
    deleted_company = crud_property_company.property_company.remove(db, id=company_id)
    return deleted_company 