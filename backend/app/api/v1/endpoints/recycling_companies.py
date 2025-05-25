from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.recycling_company import RecyclingCompanyType, RecyclingCompany, RecyclingCompanyStatus # Import Status enum
from app.models.recycling_manager import RecyclingRole
from app.schemas.recycling_company import (
    RecyclingCompanyCreate, 
    RecyclingCompanyUpdate, 
    RecyclingCompanyResponse,
    RecyclingCompanyStatusUpdate
)
# We will need RecyclingManager CRUD and schemas for manager operations, but not directly in company CRUD
from app.crud import crud_recycling_company, crud_recycling_manager, crud_user 

router = APIRouter()

@router.post("/", response_model=RecyclingCompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_recycling_company(
    *,
    db: Session = Depends(get_db),
    company_in: RecyclingCompanyCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """创建新的回收公司。创建者将自动成为该公司的一名主要管理人员。"""
    if not current_user.is_superuser and current_user.role != UserRole.RECYCLING:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限执行此操作 (需要超级用户或回收角色)"
        )

    existing_company = crud_recycling_company.recycling_company.get_by_name(db, name=company_in.name)
    if existing_company:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Recycling company '{company_in.name}' already exists.")

    company = crud_recycling_company.recycling_company.create_with_primary_manager(
        db=db, obj_in=company_in, primary_manager_user_id=current_user.id
    )
    return RecyclingCompanyResponse.model_validate(company).model_dump()

@router.get("/", response_model=List[RecyclingCompanyResponse])
async def read_recycling_companies(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    active_only: bool = Query(False, description="仅显示正常运营(active)的公司"),
    company_type: Optional[str] = Query(None, description="按公司类型过滤"),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取回收公司列表。"""
    if current_user.is_superuser:
        if active_only:
            companies = crud_recycling_company.recycling_company.get_active_companies(db, skip=skip, limit=limit)
        elif company_type:
            try:
                type_enum = RecyclingCompanyType(company_type)
                companies = crud_recycling_company.recycling_company.get_by_company_type(db, company_type=type_enum, skip=skip, limit=limit)
            except ValueError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"无效的回收公司类型: {company_type}")
        else:
            companies = crud_recycling_company.recycling_company.get_multi(db, skip=skip, limit=limit)
    elif current_user.role == UserRole.RECYCLING:
        # 回收用户查看自己关联的公司
        companies = crud_recycling_company.recycling_company.get_by_manager_user(
            db, manager_user_id=current_user.id, skip=skip, limit=limit
        )
        # Further filter by active_only or company_type if needed from the user's list
        if active_only:
            companies = [c for c in companies if c.status == RecyclingCompanyStatus.ACTIVE and c.is_active]
        if company_type:
            try:
                type_enum = RecyclingCompanyType(company_type)
                companies = [c for c in companies if c.company_type == type_enum]
            except ValueError:
                 # Should not happen if type_enum is validated before, but as a safeguard
                pass 
    else:
        # Public view: perhaps only active companies
        # companies = crud_recycling_company.recycling_company.get_active_companies(db, skip=skip, limit=limit)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权查看回收公司列表")
    return [RecyclingCompanyResponse.model_validate(c).model_dump() for c in companies]

@router.get("/{company_id}", response_model=RecyclingCompanyResponse)
async def read_recycling_company(
    *,
    db: Session = Depends(get_db),
    company_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取指定回收公司信息。"""
    company = crud_recycling_company.recycling_company.get(db, id=company_id) # Use basic get
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recycling company not found.")
    
    can_view = False
    if current_user.is_superuser:
        can_view = True
    elif current_user.role == UserRole.RECYCLING:
        assoc = crud_recycling_manager.recycling_manager.get_by_company_and_manager_user(
            db, recycling_company_id=company_id, manager_user_id=current_user.id
        )
        if assoc:
            can_view = True
    
    # Potentially allow other roles (e.g. transport companies for planning) to view basic info
    # For now, strict access.
    if not can_view:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权查看此回收公司信息")
    return RecyclingCompanyResponse.model_validate(company).model_dump()

@router.put("/{company_id}", response_model=RecyclingCompanyResponse)
async def update_recycling_company(
    *,
    db: Session = Depends(get_db),
    company_id: int,
    company_in: RecyclingCompanyUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """更新回收公司信息。"""
    company = crud_recycling_company.recycling_company.get(db, id=company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recycling company not found.")
    
    can_update = False
    if current_user.is_superuser:
        can_update = True
    else:
        manager_assoc = crud_recycling_manager.recycling_manager.get_by_company_and_manager_user(
            db, recycling_company_id=company_id, manager_user_id=current_user.id
        )
        if manager_assoc and manager_assoc.is_primary:
            can_update = True
            
    if not can_update:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this recycling company.")
    
    # Check for name uniqueness if name is being changed
    if company_in.name and company_in.name != company.name:
        existing_company = crud_recycling_company.recycling_company.get_by_name(db, name=company_in.name)
        if existing_company and existing_company.id != company_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Recycling company name '{company_in.name}' already exists.")
            
    updated_company = crud_recycling_company.recycling_company.update(db, db_obj=company, obj_in=company_in)
    return RecyclingCompanyResponse.model_validate(updated_company).model_dump()

@router.put("/{company_id}/status", response_model=RecyclingCompanyResponse)
async def update_recycling_company_operational_status(
    *,
    db: Session = Depends(get_db),
    company_id: int,
    status_in: RecyclingCompanyStatusUpdate, 
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """更新回收公司的运营状态。"""
    company = crud_recycling_company.recycling_company.get(db, id=company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recycling company not found.")

    can_update_status = False
    if current_user.is_superuser:
        can_update_status = True
    else:
        # Primary manager or specific roles (e.g. supervisor) of this company can update status
        manager_assoc = crud_recycling_manager.recycling_manager.get_by_company_and_manager_user(
            db, recycling_company_id=company_id, manager_user_id=current_user.id
        )
        if manager_assoc and (manager_assoc.is_primary or manager_assoc.role == RecyclingRole.SUPERVISOR): # Assuming SUPERVISOR can change status
            can_update_status = True
    
    if not can_update_status:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update operational status for this company.")

    updated_company = crud_recycling_company.recycling_company.update_company_status(db, db_obj=company, status_in=status_in)
    return RecyclingCompanyResponse.model_validate(updated_company).model_dump()


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recycling_company(
    *,
    db: Session = Depends(get_db),
    company_id: int,
    current_user: User = Depends(get_current_active_user)
) -> None:
    """删除回收公司。"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only superusers can delete recycling companies.")

    company = crud_recycling_company.recycling_company.get(db, id=company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recycling company not found.")

    # Add check: cannot delete if there are active orders associated? Or handle cascade.
    # For now, direct delete.
    crud_recycling_company.recycling_company.remove(db, id=company_id)
    return 