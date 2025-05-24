from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_active_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.property import Property
from app.models.property_manager import PropertyManager
from app.schemas.property import PropertyCreate, PropertyUpdate, PropertyResponse
from app.schemas.property_manager import PropertyManagerCreate, PropertyManagerUpdate, PropertyManagerResponse
from app.crud.crud_property import property as crud_property
from app.crud.crud_property_manager import property_manager as crud_prop_manager

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

# 获取物业的物业管理员列表
@router.get("/{property_id}/managers", response_model=List[PropertyManagerResponse])
async def read_property_managers(
    *,
    db: Session = Depends(get_db),
    property_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取物业的物业管理员列表"""
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
                detail="只有物业管理员或管理员可以查看物业管理员列表"
            )
        # 检查当前用户是否是物业的管理员
        is_manager = any(
            manager.manager_id == current_user.id
            for manager in property_obj.property_managers
        )
        if not is_manager:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有足够的权限查看此物业的物业管理员列表"
            )
    
    return property_obj.property_managers


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
    
    # 权限检查：只有物业总公司的主管 (is_superuser) 或该物业的物业主管 (is_primary) 可以添加新的物业人员。
    # 根据您的需求文档："物业主管...可以增删改查该物业的物业人员"
    # "物业总公司管理权限...设置物业公司的主管人员"
    
    is_authorized_to_add = False
    if current_user.is_superuser:
        is_authorized_to_add = True
    else:
        # 检查当前用户是否是该物业的主要管理员 (PropertyManager.is_primary)
        current_user_as_manager = crud_prop_manager.get_by_property_and_manager(
            db, property_id=property_id, manager_id=current_user.id
        )
        if current_user_as_manager and current_user_as_manager.is_primary:
            is_authorized_to_add = True

    if not is_authorized_to_add:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有超级管理员或物业主要管理员可以添加物业人员"
        )

    # 检查要添加的 manager_id (User.id) 是否已经存在于该物业
    existing_manager_for_user = crud_prop_manager.get_by_property_and_manager(
        db, property_id=property_id, manager_id=manager_in.manager_id
    )
    if existing_manager_for_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"用户 {manager_in.manager_id} 已经是该物业的管理员。"
        )
        
    # 如果要添加的是主要管理员，且该物业已存在主要管理员，则应阻止
    if manager_in.is_primary:
        # 检查该物业是否已有主要管理员
        # 这里需要一个方法来获取物业的主要管理员，或者遍历 property_obj.property_managers
        existing_primary_manager = db.query(PropertyManager).filter(
            PropertyManager.property_id == property_id,
            PropertyManager.is_primary == True
        ).first()
        if existing_primary_manager:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该物业已存在一个主要管理员。"
            )
            
    # 使用新的 crud_prop_manager.create
    # HTTPException 会在 CRUD 层被抛出，所以这里不需要 try-except ValueError
    manager = crud_prop_manager.create(db, obj_in=manager_in, property_id=property_id)
    return manager

# 更新物业管理员
@router.put("/{property_id}/managers/{pm_id}", response_model=PropertyManagerResponse)  # pm_id 指 PropertyManager.id
async def update_property_manager(
    *,
    db: Session = Depends(get_db),
    property_id: int,
    pm_id: int, # 这是 PropertyManager 表的 ID
    manager_in: PropertyManagerUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """更新物业管理员信息"""
    # 获取要更新的 PropertyManager 对象
    db_manager = crud_prop_manager.get(db, id=pm_id)
    if not db_manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="物业管理员记录不存在"
        )
    
    # 校验该管理员记录是否属于目标物业
    if db_manager.property_id != property_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, # 或者 404 / 403
            detail="物业管理员记录与指定的物业不匹配"
        )

    # 权限检查：类似于添加操作
    is_authorized_to_update = False
    if current_user.is_superuser:
        is_authorized_to_update = True
    else:
        current_user_as_manager = crud_prop_manager.get_by_property_and_manager(
            db, property_id=property_id, manager_id=current_user.id
        )
        if current_user_as_manager and current_user_as_manager.is_primary:
            is_authorized_to_update = True
            
    # 物业人员不能更新自己为主要管理员，除非本身就是主要管理员（这种场景下 is_primary 不变）
    # 并且，物业主管不能把自己更新为非主管，除非有其他主管。这里简化：不允许主管取消自己的主管身份。
    if db_manager.manager_id == current_user.id and manager_in.is_primary is False and db_manager.is_primary is True:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="主要管理员不能将自己降级为普通管理员。"
        )
    
    # 如果被操作的是当前用户自己，且不是主管，则不允许更改 is_primary 字段
    if db_manager.manager_id == current_user.id and not (current_user_as_manager and current_user_as_manager.is_primary) and manager_in.is_primary is not None:
        if db_manager.is_primary != manager_in.is_primary :
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="普通管理员不能修改自己的主要管理员状态。"
            )

    if not is_authorized_to_update:
        # 如果不是超管或物业主管，但操作的是自己的记录（非is_primary字段），允许吗？
        # 您的需求 "物业人员...可以查看当前小区的清运订单，可以确认清运订单的时间。" 未提及自我更新。
        # 通常普通用户不能更新自己的角色或权限。
        # 如果允许自我更新某些字段（如role, community_id），需要额外逻辑。
        # 此处严格执行：只有超管或物业主管可更新。
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有超级管理员或物业主要管理员可以更新物业人员信息"
        )
        
    # 如果尝试将一个人员设置为主要管理员，需要检查该物业是否已有其他主要管理员
    # (除非被更新者已经是主要管理员，这时 is_primary 可能为 None 或 True)
    if manager_in.is_primary is True and (not db_manager.is_primary): # 从非主管更新为主管
        existing_primary_manager = db.query(PropertyManager).filter(
            PropertyManager.property_id == property_id,
            PropertyManager.is_primary == True,
            PropertyManager.id != pm_id  # 排除当前正在更新的记录
        ).first()
        if existing_primary_manager:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该物业已存在一个主要管理员。请先将现有主要管理员降级。"
            )

    # 使用新的 crud_prop_manager.update
    # HTTPException 会在 CRUD 层被抛出
    updated_manager = crud_prop_manager.update(db, db_obj=db_manager, obj_in=manager_in)
    return updated_manager

# 移除物业管理员
@router.delete("/{property_id}/managers/{pm_id}", response_model=PropertyManagerResponse) # pm_id 指 PropertyManager.id
async def remove_property_manager(
    *,
    db: Session = Depends(get_db),
    property_id: int,
    pm_id: int, # 这是 PropertyManager 表的 ID
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """移除物业管理员"""
    # 获取要删除的 PropertyManager 对象
    db_manager = crud_prop_manager.get(db, id=pm_id) # 使用 pm_id
    if not db_manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="物业管理员记录不存在"
        )

    # 校验该管理员记录是否属于目标物业
    if db_manager.property_id != property_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="物业管理员记录与指定的物业不匹配"
        )
        
    # 权限检查
    is_authorized_to_delete = False
    if current_user.is_superuser:
        is_authorized_to_delete = True
    else:
        current_user_as_manager = crud_prop_manager.get_by_property_and_manager(
            db, property_id=property_id, manager_id=current_user.id
        )
        if current_user_as_manager and current_user_as_manager.is_primary:
            is_authorized_to_delete = True
            
    # 不能删除自己
    if db_manager.manager_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="不能移除自己。"
        )
        
    # 主要管理员不能被轻易删除，除非他是最后一个管理员？或者业务上允许直接删除。
    # 如果被删除的是主要管理员，需要有额外逻辑，例如确保有其他管理员或该物业不再需要管理员。
    # 这里简化：如果删除的是主要管理员，直接删除。
    if db_manager.is_primary:
        # log or specific handling if needed
        pass


    if not is_authorized_to_delete:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有超级管理员或物业主要管理员可以移除物业人员"
        )

    removed_manager = crud_prop_manager.remove(db, id=pm_id)
    return removed_manager