from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_active_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.order import Order, OrderStatus
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderStatusUpdate
from app.crud.crud_order import order as crud_order

router = APIRouter()

# 创建订单
@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    *,
    db: Session = Depends(get_db),
    order_in: OrderCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """创建新订单"""
    # 只有客户可以创建订单
    if current_user.role != UserRole.CUSTOMER and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限执行此操作"
        )
    
    # 创建订单
    order = crud_order.create_with_customer(
        db=db, obj_in=order_in, customer_id=current_user.id
    )
    return order

# 获取所有订单
@router.get("/", response_model=List[OrderResponse])
async def read_orders(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="订单状态过滤"),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取订单列表"""
    # 根据用户角色返回不同的订单列表
    if current_user.is_superuser:
        # 管理员可以查看所有订单
        orders = crud_order.get_multi(db, skip=skip, limit=limit, status=status)
    elif current_user.role == UserRole.CUSTOMER:
        # 客户只能查看自己的订单
        orders = crud_order.get_by_customer(
            db, customer_id=current_user.id, skip=skip, limit=limit, status=status
        )
    elif current_user.role == UserRole.PROPERTY:
        # 物业管理员查看相关小区的订单
        orders = crud_order.get_by_property_manager(
            db, manager_id=current_user.id, skip=skip, limit=limit, status=status
        )
    elif current_user.role == UserRole.TRANSPORT:
        # 运输管理员查看分配给自己的订单
        orders = crud_order.get_by_transport_manager(
            db, manager_id=current_user.id, skip=skip, limit=limit, status=status
        )
    elif current_user.role == UserRole.RECYCLING:
        # 回收站管理员查看分配给自己的订单
        orders = crud_order.get_by_recycling_manager(
            db, manager_id=current_user.id, skip=skip, limit=limit, status=status
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限执行此操作"
        )
    
    return orders

# 获取单个订单详情
@router.get("/{order_id}", response_model=OrderResponse)
async def read_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取订单详情"""
    order = crud_order.get(db, id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    # 检查权限
    if not current_user.is_superuser:
        if current_user.role == UserRole.CUSTOMER and order.customer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有足够的权限查看此订单"
            )
        elif current_user.role == UserRole.PROPERTY and order.property_manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有足够的权限查看此订单"
            )
        elif current_user.role == UserRole.TRANSPORT and order.transport_manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有足够的权限查看此订单"
            )
        elif current_user.role == UserRole.RECYCLING and order.recycling_manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有足够的权限查看此订单"
            )
    
    return order

# 更新订单状态
@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    status_update: OrderStatusUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """更新订单状态"""
    order = crud_order.get(db, id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    # 检查权限和状态流转逻辑
    current_status = order.status
    new_status = status_update.status
    
    # 管理员可以更改任何状态
    if current_user.is_superuser:
        pass
    # 物业确认
    elif new_status == OrderStatus.PROPERTY_CONFIRMED:
        if current_user.role != UserRole.PROPERTY:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有物业管理员可以确认订单"
            )
        if current_status != OrderStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能从待处理状态更改为物业确认状态"
            )
    # 分配运输
    elif new_status == OrderStatus.TRANSPORT_ASSIGNED:
        if current_user.role != UserRole.TRANSPORT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有运输管理员可以分配运输"
            )
        if current_status != OrderStatus.PROPERTY_CONFIRMED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能从物业确认状态更改为已分配运输状态"
            )
    # 运输中
    elif new_status == OrderStatus.TRANSPORTING:
        if current_user.role != UserRole.TRANSPORT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有运输管理员可以更新为运输中状态"
            )
        if current_status != OrderStatus.TRANSPORT_ASSIGNED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能从已分配运输状态更改为运输中状态"
            )
    # 已送达回收站
    elif new_status == OrderStatus.DELIVERED:
        if current_user.role != UserRole.TRANSPORT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有运输管理员可以更新为已送达状态"
            )
        if current_status != OrderStatus.TRANSPORTING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能从运输中状态更改为已送达状态"
            )
    # 回收站确认
    elif new_status == OrderStatus.RECYCLING_CONFIRMED:
        if current_user.role != UserRole.RECYCLING:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有回收站管理员可以确认回收"
            )
        if current_status != OrderStatus.DELIVERED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能从已送达状态更改为回收站确认状态"
            )
    # 完成
    elif new_status == OrderStatus.COMPLETED:
        if current_user.role != UserRole.RECYCLING:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有回收站管理员可以完成订单"
            )
        if current_status != OrderStatus.RECYCLING_CONFIRMED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能从回收站确认状态更改为完成状态"
            )
    # 取消
    elif new_status == OrderStatus.CANCELLED:
        # 客户可以取消待处理的订单
        if current_user.role == UserRole.CUSTOMER:
            if current_status != OrderStatus.PENDING:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="客户只能取消待处理状态的订单"
                )
            if order.customer_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="只能取消自己的订单"
                )
        # 物业可以取消待处理或物业确认的订单
        elif current_user.role == UserRole.PROPERTY:
            if current_status not in [OrderStatus.PENDING, OrderStatus.PROPERTY_CONFIRMED]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="物业只能取消待处理或物业确认状态的订单"
                )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的状态更新"
        )
    
    # 更新订单状态
    order_update = OrderUpdate(
        status=new_status,
        **status_update.dict(exclude={"status"})
    )
    
    # 根据角色更新相应的管理员ID
    if current_user.role == UserRole.PROPERTY and order.property_manager_id is None:
        order_update.property_manager_id = current_user.id
    elif current_user.role == UserRole.TRANSPORT and order.transport_manager_id is None:
        order_update.transport_manager_id = current_user.id
    elif current_user.role == UserRole.RECYCLING and order.recycling_manager_id is None:
        order_update.recycling_manager_id = current_user.id
    
    updated_order = crud_order.update(db, db_obj=order, obj_in=order_update)
    return updated_order

# 更新订单信息
@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    order_in: OrderUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """更新订单信息"""
    order = crud_order.get(db, id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    # 检查权限
    if not current_user.is_superuser:
        # 客户只能更新自己的待处理订单
        if current_user.role == UserRole.CUSTOMER:
            if order.customer_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="只能更新自己的订单"
                )
            if order.status != OrderStatus.PENDING:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="只能更新待处理状态的订单"
                )
        # 物业只能更新物业相关信息
        elif current_user.role == UserRole.PROPERTY:
            if order.status not in [OrderStatus.PENDING, OrderStatus.PROPERTY_CONFIRMED]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="只能更新待处理或物业确认状态的订单"
                )
            # 限制物业只能更新物业相关字段
            allowed_fields = {"property_notes", "status"}
            for field in order_in.__dict__:
                if field not in allowed_fields and getattr(order_in, field) is not None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"物业管理员不能更新{field}字段"
                    )
        # 运输只能更新运输相关信息
        elif current_user.role == UserRole.TRANSPORT:
            if order.status not in [OrderStatus.PROPERTY_CONFIRMED, OrderStatus.TRANSPORT_ASSIGNED, OrderStatus.TRANSPORTING]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="只能更新物业确认、已分配运输或运输中状态的订单"
                )
            # 限制运输只能更新运输相关字段
            allowed_fields = {"driver_id", "vehicle_plate", "transport_route", "transport_notes", "status", "actual_pickup_time", "delivery_time"}
            for field in order_in.__dict__:
                if field not in allowed_fields and getattr(order_in, field) is not None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"运输管理员不能更新{field}字段"
                    )
        # 回收站只能更新回收相关信息
        elif current_user.role == UserRole.RECYCLING:
            if order.status not in [OrderStatus.DELIVERED, OrderStatus.RECYCLING_CONFIRMED]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="只能更新已送达或回收站确认状态的订单"
                )
            # 限制回收站只能更新回收相关字段
            allowed_fields = {"recycling_notes", "status", "waste_weight", "recycling_confirm_time"}
            for field in order_in.__dict__:
                if field not in allowed_fields and getattr(order_in, field) is not None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"回收站管理员不能更新{field}字段"
                    )
    
    updated_order = crud_order.update(db, db_obj=order, obj_in=order_in)
    return updated_order

# 删除订单
@router.delete("/{order_id}", response_model=OrderResponse)
async def delete_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """删除订单"""
    order = crud_order.get(db, id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    # 只有管理员或者客户可以删除待处理的订单
    if not current_user.is_superuser:
        if current_user.role != UserRole.CUSTOMER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有客户或管理员可以删除订单"
            )
        if order.customer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能删除自己的订单"
            )
        if order.status != OrderStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能删除待处理状态的订单"
            )
    
    order = crud_order.remove(db, id=order_id)
    return order