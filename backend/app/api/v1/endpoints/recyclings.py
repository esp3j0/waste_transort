from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_active_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.recycling import Recycling, RecyclingStatus
from app.schemas.recycling import RecyclingCreate, RecyclingUpdate, RecyclingResponse, RecyclingStatusUpdate
from app.crud.crud_recycling import recycling as crud_recycling

router = APIRouter()

# 创建回收站信息
@router.post("/", response_model=RecyclingResponse, status_code=status.HTTP_201_CREATED)
async def create_recycling(
    *,
    db: Session = Depends(get_db),
    recycling_in: RecyclingCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """创建新回收站信息"""
    # 只有管理员或回收站角色可以创建回收站信息
    if current_user.role != UserRole.RECYCLING and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限执行此操作"
        )
    
    # 创建回收站信息
    recycling_obj = crud_recycling.create_with_manager(
        db=db, obj_in=recycling_in, manager_id=current_user.id
    )
    return recycling_obj

# 获取所有回收站信息
@router.get("/", response_model=List[RecyclingResponse])
async def read_recyclings(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="回收站状态过滤"),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取回收站信息列表"""
    # 根据用户角色返回不同的回收站信息列表
    if current_user.is_superuser:
        # 管理员可以查看所有回收站信息
        recyclings = crud_recycling.get_multi(db, skip=skip, limit=limit, status=status)
    elif current_user.role == UserRole.RECYCLING:
        # 回收站管理员只能查看自己管理的回收站
        recyclings = crud_recycling.get_by_manager(
            db, manager_id=current_user.id, skip=skip, limit=limit, status=status
        )
    else:
        # 其他角色可以查看所有回收站的基本信息
        recyclings = crud_recycling.get_multi(db, skip=skip, limit=limit, status=status)
    
    return recyclings

# 获取单个回收站详情
@router.get("/{recycling_id}", response_model=RecyclingResponse)
async def read_recycling(
    *,
    db: Session = Depends(get_db),
    recycling_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取回收站详情"""
    recycling_obj = crud_recycling.get(db, id=recycling_id)
    if not recycling_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="回收站信息不存在"
        )
    
    # 检查权限
    if not current_user.is_superuser and current_user.role == UserRole.RECYCLING:
        if recycling_obj.manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有足够的权限查看此回收站信息"
            )
    
    return recycling_obj

# 更新回收站信息
@router.put("/{recycling_id}", response_model=RecyclingResponse)
async def update_recycling(
    *,
    db: Session = Depends(get_db),
    recycling_id: int,
    recycling_in: RecyclingUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """更新回收站信息"""
    recycling_obj = crud_recycling.get(db, id=recycling_id)
    if not recycling_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="回收站信息不存在"
        )
    
    # 检查权限
    if not current_user.is_superuser:
        if current_user.role != UserRole.RECYCLING:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有回收站管理员或管理员可以更新回收站信息"
            )
        if recycling_obj.manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能更新自己管理的回收站信息"
            )
    
    updated_recycling = crud_recycling.update(db, db_obj=recycling_obj, obj_in=recycling_in)
    return updated_recycling

# 更新回收站状态
@router.put("/{recycling_id}/status", response_model=RecyclingResponse)
async def update_recycling_status(
    *,
    db: Session = Depends(get_db),
    recycling_id: int,
    status_update: RecyclingStatusUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """更新回收站状态"""
    recycling_obj = crud_recycling.get(db, id=recycling_id)
    if not recycling_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="回收站信息不存在"
        )
    
    # 检查权限
    if not current_user.is_superuser:
        if current_user.role != UserRole.RECYCLING:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有回收站管理员或管理员可以更新回收站状态"
            )
        if recycling_obj.manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能更新自己管理的回收站状态"
            )
    
    recycling_update = RecyclingUpdate(status=status_update.status)
    updated_recycling = crud_recycling.update(db, db_obj=recycling_obj, obj_in=recycling_update)
    return updated_recycling

# 删除回收站信息
@router.delete("/{recycling_id}", response_model=RecyclingResponse)
async def delete_recycling(
    *,
    db: Session = Depends(get_db),
    recycling_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """删除回收站信息"""
    recycling_obj = crud_recycling.get(db, id=recycling_id)
    if not recycling_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="回收站信息不存在"
        )
    
    # 只有管理员可以删除回收站信息
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以删除回收站信息"
        )
    
    recycling_obj = crud_recycling.remove(db, id=recycling_id)
    return recycling_obj