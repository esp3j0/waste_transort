from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.crud.crud_community import community
from app.crud import crud_property_manager
from app.models.user import User, UserRole
from app.models.property_manager import PropertyManager
from app.schemas.community import (
    CommunityCreate,
    CommunityUpdate,
    CommunityResponse
)

router = APIRouter()

@router.post("/", response_model=CommunityResponse, status_code=status.HTTP_201_CREATED)
async def create_community(
    *,
    db: Session = Depends(get_db),
    community_in: CommunityCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    创建新社区
    """
    can_create = False
    if current_user.is_superuser:
        can_create = True
    elif current_user.role == UserRole.PROPERTY:
        if community_in.property_company_id:
            # Check if current_user is a primary manager of the target property_company_id
            primary_manager_assoc = crud_property_manager.property_manager.get_primary_manager_for_company(
                db, property_company_id=community_in.property_company_id
            )
            if primary_manager_assoc and primary_manager_assoc.manager_id == current_user.id:
                can_create = True
        else:
            # If property_company_id is not provided in input, this might be an issue or handled by CRUD
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Property company ID is required to create a community.")

    if not can_create:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，只有超级管理员或物业公司的主要管理员可以创建社区。"
        )
    
    community_obj = community.get_by_name(db, name=community_in.name)
    if community_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="社区名称已存在"
        )
    
    db_community = community.create_with_property_company(db, obj_in=community_in)
    return CommunityResponse.model_validate(db_community).model_dump()

@router.get("/", response_model=List[CommunityResponse])
async def read_communities(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    获取社区列表 (所有已认证用户均可访问)
    """
    communities = community.get_multi(db, skip=skip, limit=limit)
    return [
        CommunityResponse.model_validate(c).model_dump() for c in communities
    ]

@router.get("/{community_id}", response_model=CommunityResponse)
async def read_community(
    *,
    db: Session = Depends(get_db),
    community_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    获取指定社区信息 (所有已认证用户均可访问)
    """
    community_obj = community.get(db, id=community_id)
    if not community_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社区不存在"
        )
    # No specific role-based access restriction for reading individual community
    return CommunityResponse.model_validate(community_obj).model_dump()

@router.put("/{community_id}", response_model=CommunityResponse)
async def update_community(
    *,
    db: Session = Depends(get_db),
    community_id: int,
    community_in: CommunityUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    更新社区信息
    """
    community_obj = community.get(db, id=community_id)
    if not community_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社区不存在"
        )
    
    can_update = False
    if current_user.is_superuser:
        can_update = True
    elif current_user.role == UserRole.PROPERTY:
        if community_obj.property_company_id:
            # Check if current_user is a primary manager of the community's property_company
            primary_manager_assoc = crud_property_manager.property_manager.get_primary_manager_for_company(
                db, property_company_id=community_obj.property_company_id
            )
            if primary_manager_assoc and primary_manager_assoc.manager_id == current_user.id:
                can_update = True

    if not can_update:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足，只有超级管理员或该社区所属物业公司的主要管理员可以更新。")

    updated_community = community.update(db, db_obj=community_obj, obj_in=community_in)
    return CommunityResponse.model_validate(updated_community).model_dump()

@router.delete("/{community_id}", response_model=CommunityResponse)
async def delete_community(
    *,
    db: Session = Depends(get_db),
    community_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    删除社区
    """
    community_obj = community.get(db, id=community_id)
    if not community_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社区不存在"
        )
    
    can_delete = False
    if current_user.is_superuser:
        can_delete = True
    elif current_user.role == UserRole.PROPERTY:
        if community_obj.property_company_id:
            # Check if current_user is a primary manager of the community's property_company
            primary_manager_assoc = crud_property_manager.property_manager.get_primary_manager_for_company(
                db, property_company_id=community_obj.property_company_id
            )
            if primary_manager_assoc and primary_manager_assoc.manager_id == current_user.id:
                can_delete = True
    
    if not can_delete:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，只有超级管理员或该社区所属物业公司的主要管理员可以删除。"
        )
    
    # The community.remove in CRUD likely returns the removed object or True/None.
    # For HTTP 204, we should not return a body.
    community.remove(db, id=community_id)
    # Return the object for now as per original response_model, will adjust if 204 is preferred
    return community_obj # Or raise HTTPException(status_code=status.HTTP_204_NO_CONTENT) if no body 