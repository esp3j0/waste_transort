from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_active_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.transport import Transport, DriverStatus
from app.schemas.transport import TransportCreate, TransportUpdate, TransportResponse, DriverStatusUpdate
from app.crud.crud_transport import transport as crud_transport

router = APIRouter()

# 创建运输信息
@router.post("/", response_model=TransportResponse, status_code=status.HTTP_201_CREATED)
async def create_transport(
    *,
    db: Session = Depends(get_db),
    transport_in: TransportCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """创建新运输信息"""
    # 只有管理员或运输角色可以创建运输信息
    if current_user.role != UserRole.TRANSPORT and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限执行此操作"
        )
    
    # 创建运输信息
    transport_obj = crud_transport.create_with_manager(
        db=db, obj_in=transport_in, manager_id=current_user.id
    )
    return transport_obj

# 获取所有运输信息
@router.get("/", response_model=List[TransportResponse])
async def read_transports(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="司机状态过滤"),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取运输信息列表"""
    # 根据用户角色返回不同的运输信息列表
    if current_user.is_superuser:
        # 管理员可以查看所有运输信息
        transports = crud_transport.get_multi(db, skip=skip, limit=limit, status=status)
    elif current_user.role == UserRole.TRANSPORT:
        # 运输管理员只能查看自己管理的运输
        transports = crud_transport.get_by_manager(
            db, manager_id=current_user.id, skip=skip, limit=limit, status=status
        )
    else:
        # 其他角色可以查看所有运输的基本信息
        transports = crud_transport.get_multi(db, skip=skip, limit=limit, status=status)
    
    return transports

# 获取单个运输详情
@router.get("/{transport_id}", response_model=TransportResponse)
async def read_transport(
    *,
    db: Session = Depends(get_db),
    transport_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取运输详情"""
    transport_obj = crud_transport.get(db, id=transport_id)
    if not transport_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="运输信息不存在"
        )
    
    # 检查权限
    if not current_user.is_superuser and current_user.role == UserRole.TRANSPORT:
        if transport_obj.manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有足够的权限查看此运输信息"
            )
    
    return transport_obj

# 更新运输信息
@router.put("/{transport_id}", response_model=TransportResponse)
async def update_transport(
    *,
    db: Session = Depends(get_db),
    transport_id: int,
    transport_in: TransportUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """更新运输信息"""
    transport_obj = crud_transport.get(db, id=transport_id)
    if not transport_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="运输信息不存在"
        )
    
    # 检查权限
    if not current_user.is_superuser:
        if current_user.role != UserRole.TRANSPORT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有运输管理员或管理员可以更新运输信息"
            )
        if transport_obj.manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能更新自己管理的运输信息"
            )
    
    updated_transport = crud_transport.update(db, db_obj=transport_obj, obj_in=transport_in)
    return updated_transport

# 更新司机状态
@router.put("/{transport_id}/status", response_model=TransportResponse)
async def update_driver_status(
    *,
    db: Session = Depends(get_db),
    transport_id: int,
    status_update: DriverStatusUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """更新司机状态"""
    transport_obj = crud_transport.get(db, id=transport_id)
    if not transport_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="运输信息不存在"
        )
    
    # 检查权限
    if not current_user.is_superuser:
        if current_user.role != UserRole.TRANSPORT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有运输管理员或管理员可以更新司机状态"
            )
        if transport_obj.manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能更新自己管理的司机状态"
            )
    
    transport_update = TransportUpdate(driver_status=status_update.status)
    updated_transport = crud_transport.update(db, db_obj=transport_obj, obj_in=transport_update)
    return updated_transport

# 删除运输信息
@router.delete("/{transport_id}", response_model=TransportResponse)
async def delete_transport(
    *,
    db: Session = Depends(get_db),
    transport_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """删除运输信息"""
    transport_obj = crud_transport.get(db, id=transport_id)
    if not transport_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="运输信息不存在"
        )
    
    # 只有管理员可以删除运输信息
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以删除运输信息"
        )
    
    transport_obj = crud_transport.remove(db, id=transport_id)
    return transport_obj