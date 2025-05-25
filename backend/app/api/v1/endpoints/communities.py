from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.crud.crud_community import community
from app.models.user import User, UserRole
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
    # 检查权限
    if current_user.role not in [UserRole.ADMIN, UserRole.PROPERTY]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 检查社区名称是否已存在
    community_obj = community.get_by_name(db, name=community_in.name)
    if community_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="社区名称已存在"
        )
    
    # 创建社区
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
    获取社区列表
    """
    if current_user.role == UserRole.PROPERTY:
        # 物业用户只能看到自己管理的社区
        communities = community.get_by_property(
            db, property_id=current_user.property_id, skip=skip, limit=limit
        )
    else:
        # 管理员可以看到所有社区
        communities = community.get_multi(db, skip=skip, limit=limit)
    return [
        CommunityResponse.model_validate(community).model_dump() for community in communities
    ]

@router.get("/{community_id}", response_model=CommunityResponse)
async def read_community(
    *,
    db: Session = Depends(get_db),
    community_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    获取指定社区信息
    """
    community_obj = community.get(db, id=community_id)
    if not community_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社区不存在"
        )
    
    # 检查权限
    if current_user.role == UserRole.PROPERTY and community_obj.property_id != current_user.property_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该社区信息"
        )
    
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
    
    # 检查权限
    if current_user.role == UserRole.PROPERTY and community_obj.property_id != current_user.property_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改该社区信息"
        )
    
    # Permission check: Only superuser or primary manager of the property company can update
    can_update = False
    if current_user.is_superuser:
        can_update = True
    else:
        if community_obj.property_company_id:
            primary_manager = community.get_primary_manager_for_company(
                db, property_company_id=community_obj.property_company_id
            )
            if primary_manager and primary_manager.manager_id == current_user.id:
                can_update = True

    if not can_update:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this community")

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
    
    # 检查权限
    if current_user.role not in [UserRole.ADMIN, UserRole.PROPERTY]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除社区"
        )
    
    if current_user.role == UserRole.PROPERTY and community_obj.property_id != current_user.property_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除该社区"
        )
    
    community_obj = community.remove(db, id=community_id)
    return community_obj 