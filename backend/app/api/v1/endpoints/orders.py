from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
import datetime

from app.api.deps import get_current_user, get_current_active_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.order import Order, OrderStatus
from app.models.address import Address
from app.models.property_manager import PropertyManager
from app.models.community import Community
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
    try:
        order = crud_order.create_with_customer(
            db=db, obj_in=order_in, customer_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return order

# 获取所有订单
@router.get("/", response_model=List[OrderResponse])
async def read_orders(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[OrderStatus] = Query(None, alias="status", description="订单状态过滤"),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取订单列表"""
    # 将 Pydantic Enum 转换为字符串值，如果提供了 status_filter
    status_str = status_filter.value if status_filter else None

    if current_user.is_superuser:
        orders = crud_order.get_multi(db, skip=skip, limit=limit, status=status_str)
    elif current_user.role == UserRole.CUSTOMER:
        orders = crud_order.get_by_customer(
            db, customer_id=current_user.id, skip=skip, limit=limit, status=status_str
        )
    elif current_user.role == UserRole.PROPERTY:
        # 使用新的 CRUD 方法，传递当前物业人员的 user_id
        orders = crud_order.get_by_property_manager(
            db, manager_user_id=current_user.id, skip=skip, limit=limit, status=status_str
        )
    elif current_user.role == UserRole.TRANSPORT:
        orders = crud_order.get_by_transport_manager(
            db, manager_id=current_user.id, skip=skip, limit=limit, status=status_str
        )
    elif current_user.role == UserRole.RECYCLING:
        orders = crud_order.get_by_recycling_manager(
            db, manager_id=current_user.id, skip=skip, limit=limit, status=status_str
        )
    else:
        # This case should ideally not be reached if roles are well-defined
        # or covered by a default deny in authorization layer if any.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="当前用户角色无权查看订单列表"
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
    # Eager load address and its community for permission check and response
    order = db.query(Order).options(joinedload(Order.address).joinedload(Address.community)).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    # 权限检查
    if current_user.is_superuser:
        return order # Superuser can see any order

    if current_user.role == UserRole.CUSTOMER:
        if order.customer_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有足够的权限查看此订单")
    elif current_user.role == UserRole.PROPERTY:
        # 物业人员权限检查
        if not order.address or not order.address.community_id:
             # Should not happen if data integrity is maintained (address must have community)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="订单地址信息不完整，无法验证物业权限")

        accessible_communities = set()
        pm_records = db.query(PropertyManager).filter(PropertyManager.manager_id == current_user.id).all()
        if not pm_records:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="当前物业人员未关联任何物业或小区")

        for pm_rec in pm_records:
            if pm_rec.is_primary:
                # 主管：获取其物业公司管理的所有小区
                if pm_rec.property_id:
                    property_communities = db.query(Address.community_id).distinct().join(Community).filter(Community.property_id == pm_rec.property_id).all()
                    for pc_id_tuple in property_communities:
                        accessible_communities.add(pc_id_tuple[0]) # pc_id_tuple[0] is community_id
            else:
                if pm_rec.community_id:
                    accessible_communities.add(pm_rec.community_id)
        
        if order.address.community_id not in accessible_communities:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="此订单不属于您管理的小区范围")
            
    elif current_user.role == UserRole.TRANSPORT:
        if order.transport_manager_id != current_user.id and order.driver_id != current_user.id: # Assuming driver is also a User with TRANSPORT role
             # A driver might also be a user, check if order.driver.user_id == current_user.id if Transport model has user_id
             # For now, only transport_manager_id is checked for simplicity for transport role in general.
             # If a specific driver user needs to see only their orders, that needs more granular check or a separate role.
            pass # Allow if assigned as transport manager or driver - current model links driver_id to Transport.id not User.id directly for order.
                 # The order model has driver_id -> Transport.id and transport_manager_id -> User.id
                 # So, for a User with TRANSPORT role, if they are the transport_manager_id, they can see it.
            if order.transport_manager_id != current_user.id:
                 # More complex: If current_user is a driver, check if any Transport record linked to this user is the driver_id in order
                 # This part might need refinement based on how drivers (as users) are mapped to Transport entries.
                 # For now, if not superuser and not customer, and role is transport, they must be the transport_manager_id on the order.
                 is_assigned_driver = False # Placeholder for more complex driver check if needed
                 if not is_assigned_driver and order.transport_manager_id != current_user.id:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有足够的权限查看此订单的运输信息")
    elif current_user.role == UserRole.RECYCLING:
        if order.recycling_manager_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有足够的权限查看此订单的回收信息")
    else: # Other roles not explicitly handled for GET /orders/{order_id}
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您的角色无权查看此订单详情")

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
    order_obj = crud_order.get(db, id=order_id)
    if not order_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    current_status = order_obj.status
    new_status = status_update.status
    
    # Prepare data for CRUD update, including potential auto-set fields
    update_kwargs = status_update.model_dump(exclude_unset=True) # Use model_dump for Pydantic v2+
    # Remove status from kwargs as it's passed directly to update_status CRUD method
    update_kwargs.pop("status", None) 

    # 权限和状态流转逻辑
    can_update = False
    if current_user.is_superuser:
        can_update = True
    elif new_status == OrderStatus.PROPERTY_CONFIRMED:
        if current_user.role == UserRole.PROPERTY and current_status == OrderStatus.PENDING:
            can_update = True
            update_kwargs["property_manager_id"] = current_user.id
            if "property_confirm_time" not in update_kwargs or update_kwargs["property_confirm_time"] is None:
                 update_kwargs["property_confirm_time"] = datetime.datetime.utcnow()
            # Permission to confirm: check if this order's community is accessible by this property manager
            if not order_obj.address or not order_obj.address.community_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="订单地址或小区信息不完整，无法确认。")
            
            # Verify property manager has rights to this community (similar to read_order logic)
            accessible_communities = set()
            pm_records = db.query(PropertyManager).filter(PropertyManager.manager_id == current_user.id).all()
            if not pm_records: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您未被指定为任何物业的管理员。")
            for pm_rec in pm_records:
                if pm_rec.is_primary and pm_rec.property_id:
                    communities_of_property = db.query(Community.id).filter(Community.property_id == pm_rec.property_id).all()
                    for pc_id_tuple in communities_of_property: accessible_communities.add(pc_id_tuple[0])
                elif not pm_rec.is_primary and pm_rec.community_id:
                    accessible_communities.add(pm_rec.community_id)
            if order_obj.address.community_id not in accessible_communities:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您无权确认此小区的订单。")
        else:
            detail_msg = "只有物业管理员可以将待处理订单确认为物业已确认。"
            if current_status != OrderStatus.PENDING: detail_msg = "只能从待处理状态更改为物业确认状态。"
            if current_user.role != UserRole.PROPERTY: detail_msg = "只有物业管理员可以确认订单。"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail_msg)

    # ... (Other status transitions: TRANSPORT_ASSIGNED, TRANSPORTING, DELIVERED, RECYCLING_CONFIRMED, COMPLETED)
    # Ensure to set relevant manager_ids (transport_manager_id, recycling_manager_id) and times
    elif new_status == OrderStatus.TRANSPORT_ASSIGNED:
        if current_user.role == UserRole.TRANSPORT and current_status == OrderStatus.PROPERTY_CONFIRMED:
            can_update = True
            update_kwargs["transport_manager_id"] = current_user.id
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只有运输管理员可以将物业确认的订单分配运输。")
    elif new_status == OrderStatus.TRANSPORTING:
        if current_user.role == UserRole.TRANSPORT and current_status == OrderStatus.TRANSPORT_ASSIGNED:
            can_update = True
            # actual_pickup_time might be set here or already in status_update
            if "actual_pickup_time" not in update_kwargs or update_kwargs["actual_pickup_time"] is None:
                update_kwargs["actual_pickup_time"] = datetime.datetime.utcnow()
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只有运输管理员可以将已分配运输的订单更新为运输中。")
    elif new_status == OrderStatus.DELIVERED:
        if current_user.role == UserRole.TRANSPORT and current_status == OrderStatus.TRANSPORTING:
            can_update = True
            if "delivery_time" not in update_kwargs or update_kwargs["delivery_time"] is None:
                update_kwargs["delivery_time"] = datetime.datetime.utcnow()
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只有运输管理员可以将运输中的订单更新为已送达。")
    elif new_status == OrderStatus.RECYCLING_CONFIRMED:
        if current_user.role == UserRole.RECYCLING and current_status == OrderStatus.DELIVERED:
            can_update = True
            update_kwargs["recycling_manager_id"] = current_user.id
            if "recycling_confirm_time" not in update_kwargs or update_kwargs["recycling_confirm_time"] is None:
                update_kwargs["recycling_confirm_time"] = datetime.datetime.utcnow()
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只有回收站管理员可以将已送达的订单确认为回收站已确认。")
    elif new_status == OrderStatus.COMPLETED:
        if current_user.role == UserRole.RECYCLING and current_status == OrderStatus.RECYCLING_CONFIRMED:
            can_update = True
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只有回收站管理员可以将回收站确认的订单标记为完成。")
    elif new_status == OrderStatus.CANCELLED:
        if current_user.role == UserRole.CUSTOMER and order_obj.customer_id == current_user.id and current_status == OrderStatus.PENDING:
            can_update = True
        elif current_user.role == UserRole.PROPERTY and current_status in [OrderStatus.PENDING, OrderStatus.PROPERTY_CONFIRMED]:
            # Add community access check for property manager cancelling
            can_update = True # Placeholder, add community check here too
        elif current_user.is_superuser: # Superuser can cancel most states perhaps
            can_update = True
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="订单状态无法取消或您无权取消。")
    
    if not can_update and not current_user.is_superuser: # Double check, superuser bypasses specific can_update flags
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您无权将订单更新到此状态或不满足状态流转条件。")

    updated_order = crud_order.update_status(db, db_obj=order_obj, status=new_status.value, **update_kwargs)
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
    order_obj = crud_order.get(db, id=order_id)
    if not order_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    # 权限检查
    can_edit_fields = False
    if current_user.is_superuser:
        can_edit_fields = True
    elif current_user.role == UserRole.CUSTOMER:
        if order_obj.customer_id == current_user.id and order_obj.status == OrderStatus.PENDING:
            can_edit_fields = True # Can edit anything if pending and own order
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只能更新自己且状态为待处理的订单。")
    elif current_user.role == UserRole.PROPERTY:
        # Check community access for property manager
        if not order_obj.address or not order_obj.address.community_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="订单地址或小区信息不完整。")
        accessible_communities = set()
        pm_records = db.query(PropertyManager).filter(PropertyManager.manager_id == current_user.id).all()
        if not pm_records: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您未被指定为任何物业的管理员。")
        for pm_rec in pm_records:
            if pm_rec.is_primary and pm_rec.property_id:
                communities_of_property = db.query(Community.id).filter(Community.property_id == pm_rec.property_id).all()
                for pc_id_tuple in communities_of_property: accessible_communities.add(pc_id_tuple[0])
            elif not pm_rec.is_primary and pm_rec.community_id:
                accessible_communities.add(pm_rec.community_id)
        if order_obj.address.community_id not in accessible_communities:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您无权修改此小区的订单。")
        
        if order_obj.status in [OrderStatus.PENDING, OrderStatus.PROPERTY_CONFIRMED]:
            can_edit_fields = True
            #物业只能更新特定字段
            allowed_fields_for_prop = {"property_notes"} # Add other fields if property can edit them
            update_data_dict = order_in.model_dump(exclude_unset=True)
            for field_key in update_data_dict.keys():
                if field_key not in allowed_fields_for_prop:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"物业管理员只能更新允许的字段，如备注。不允许更新 '{field_key}'.")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="物业只能更新待处理或物业已确认状态的订单。")

    # Add similar checks for TRANSPORT and RECYCLING roles and their allowed fields/statuses
    
    if not can_edit_fields:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您无权修改此订单的这些字段或当前状态不允许修改。")

    updated_order = crud_order.update(db, db_obj=order_obj, obj_in=order_in)
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
    order_obj = crud_order.get(db, id=order_id)
    if not order_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    can_delete = False
    if current_user.is_superuser:
        can_delete = True
    elif current_user.role == UserRole.CUSTOMER:
        if order_obj.customer_id == current_user.id and order_obj.status == OrderStatus.PENDING:
            can_delete = True
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="客户只能删除自己且状态为待处理的订单。")
    # Add logic if property managers can delete orders from their communities
    # elif current_user.role == UserRole.PROPERTY: ... community check ...
    
    if not can_delete:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您无权删除此订单。")
    
    deleted_order = crud_order.remove(db, id=order_id)
    return deleted_order