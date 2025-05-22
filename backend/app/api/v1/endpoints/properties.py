from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_active_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.property import Property
from app.schemas.property import (
    PropertyCreate, PropertyUpdate, PropertyResponse,
    PropertyManagerCreate, PropertyManagerUpdate, PropertyManagerResponse
)
from app.crud.crud_property import property as crud_property

router = APIRouter()

# 创建物业信息
@router.post("/", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
async def create_property(
    *,
    db: Session = Depends(get_db),
    property_in: PropertyCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """创建新物业信息"""
    # 只有管理员或物业角色可以创建物业信息
    if current_user.role != UserRole.PROPERTY and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限执行此操作"
        )
    
    # 创建物业信息
    property_obj = crud_property.create_with_manager(
        db=db, obj_in=property_in, manager_id=current_user.id
    )
    return property_obj

# 获取所有物业信息
@router.get("/", response_model=List[PropertyResponse])
async def read_properties(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取物业信息列表"""
    # 根据用户角色返回不同的物业信息列表
    if current_user.is_superuser:
        # 管理员可以查看所有物业信息
        properties = crud_property.get_multi(db, skip=skip, limit=limit)
    elif current_user.role == UserRole.PROPERTY:
        # 物业管理员只能查看自己管理的物业
        properties = crud_property.get_by_manager(
            db, manager_id=current_user.id, skip=skip, limit=limit
        )
    else:
        # 其他角色可以查看所有物业的基本信息
        properties = crud_property.get_multi(db, skip=skip, limit=limit)
    
    return properties

# 获取单个物业详情
@router.get("/{property_id}", response_model=PropertyResponse)
async def read_property(
    *,
    db: Session = Depends(get_db),
    property_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取物业详情"""
    property_obj = crud_property.get(db, id=property_id)
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="物业信息不存在"
        )
    
    # 检查权限
    if not current_user.is_superuser and current_user.role == UserRole.PROPERTY:
        # 检查用户是否是物业的管理员
        is_manager = any(
            manager.manager_id == current_user.id
            for manager in property_obj.property_managers
        )
        if not is_manager:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有足够的权限查看此物业信息"
            )
    
    return property_obj

# 更新物业信息
@router.put("/{property_id}", response_model=PropertyResponse)
async def update_property(
    *,
    db: Session = Depends(get_db),
    property_id: int,
    property_in: PropertyUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """更新物业信息"""
    property_obj = crud_property.get(db, id=property_id)
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="物业信息不存在"
        )
    
    # 检查权限
    if not current_user.is_superuser:
        if current_user.role != UserRole.PROPERTY:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有物业管理员或管理员可以更新物业信息"
            )
        # 检查用户是否是物业的管理员
        is_manager = any(
            manager.manager_id == current_user.id
            for manager in property_obj.property_managers
        )
        if not is_manager:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能更新自己管理的物业信息"
            )
    
    updated_property = crud_property.update(db, db_obj=property_obj, obj_in=property_in)
    return updated_property

# 删除物业信息
@router.delete("/{property_id}", response_model=PropertyResponse)
async def delete_property(
    *,
    db: Session = Depends(get_db),
    property_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """删除物业信息"""
    property_obj = crud_property.get(db, id=property_id)
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="物业信息不存在"
        )
    
    # 只有管理员可以删除物业信息
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以删除物业信息"
        )
    
    property_obj = crud_property.remove(db, id=property_id)
    return property_obj

# 添加物业管理员
@router.post("/{property_id}/managers", response_model=PropertyManagerResponse)
async def add_property_manager(
    *,
    db: Session = Depends(get_db),
    property_id: int,
    manager_in: PropertyManagerCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """添加物业管理员"""
    # 检查物业是否存在
    property_obj = crud_property.get(db, id=property_id)
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="物业信息不存在"
        )
    
    # 检查权限
    if not current_user.is_superuser:
        if current_user.role != UserRole.PROPERTY:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有物业管理员或管理员可以添加管理员"
            )
        # 检查当前用户是否是物业的主要管理员
        is_primary_manager = any(
            manager.manager_id == current_user.id and manager.is_primary
            for manager in property_obj.property_managers
        )
        if not is_primary_manager:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有主要管理员可以添加其他管理员"
            )
    
    try:
        manager = crud_property.add_manager(db, property_id=property_id, manager_in=manager_in)
        return manager
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# 更新物业管理员
@router.put("/{property_id}/managers/{manager_id}", response_model=PropertyManagerResponse)
async def update_property_manager(
    *,
    db: Session = Depends(get_db),
    property_id: int,
    manager_id: int,
    manager_in: PropertyManagerUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """更新物业管理员信息"""
    # 检查物业是否存在
    property_obj = crud_property.get(db, id=property_id)
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="物业信息不存在"
        )
    
    # 检查权限
    if not current_user.is_superuser:
        if current_user.role != UserRole.PROPERTY:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有物业管理员或管理员可以更新管理员信息"
            )
        # 检查当前用户是否是物业的主要管理员
        is_primary_manager = any(
            manager.manager_id == current_user.id and manager.is_primary
            for manager in property_obj.property_managers
        )
        if not is_primary_manager:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有主要管理员可以更新管理员信息"
            )
    
    try:
        manager = crud_property.update_manager(
            db, manager_id=manager_id, property_id=property_id, manager_in=manager_in
        )
        return manager
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# 移除物业管理员
@router.delete("/{property_id}/managers/{manager_id}", response_model=PropertyManagerResponse)
async def remove_property_manager(
    *,
    db: Session = Depends(get_db),
    property_id: int,
    manager_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """移除物业管理员"""
    # 检查物业是否存在
    property_obj = crud_property.get(db, id=property_id)
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="物业信息不存在"
        )
    
    # 检查权限
    if not current_user.is_superuser:
        if current_user.role != UserRole.PROPERTY:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有物业管理员或管理员可以移除管理员"
            )
        # 检查当前用户是否是物业的主要管理员
        is_primary_manager = any(
            manager.manager_id == current_user.id and manager.is_primary
            for manager in property_obj.property_managers
        )
        if not is_primary_manager:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有主要管理员可以移除其他管理员"
            )
    
    try:
        manager = crud_property.remove_manager(db, manager_id=manager_id, property_id=property_id)
        return manager
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )