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
from app.models.transport_company import TransportCompany
from app.models.transport_manager import TransportManager, TransportRole, DriverStatus
from app.models.recycling_company import RecyclingCompany
from app.models.recycling_manager import RecyclingManager
from app.models.vehicle import Vehicle, VehicleStatus
from app.models.waste_record import WasteRecord
from app.models.payment import Payment

from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderStatusUpdate
from app.schemas.transport_manager import TransportManagerResponse
from app.schemas.vehicle import VehicleResponse
from app.schemas.transport_company import TransportCompanyResponse
from app.schemas.waste_record import WasteRecordResponse
from app.schemas.payment import PaymentResponse
from app.crud.crud_order import order as crud_order
from app.crud import crud_transport_company, crud_transport_manager, crud_vehicle
from app.crud.crud_recycling_manager import recycling_manager as crud_recycling_manager
from app.crud.crud_recycling_company import recycling_company as crud_recycling_company

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
    
    # Eager load for response, including waste_records and payments
    final_order_obj = db.query(Order).options(
        joinedload(Order.address).joinedload(Address.community),
        joinedload(Order.transport_company),
        joinedload(Order.driver_association).joinedload(TransportManager.manager),
        joinedload(Order.vehicle),
        joinedload(Order.recycling_company),
        joinedload(Order.waste_records).joinedload(WasteRecord.recorded_by_user),
        joinedload(Order.payments)
    ).filter(Order.id == order.id).first()
    if not final_order_obj: # Should not happen
        raise HTTPException(status_code=500, detail="Failed to fetch created order with details")

    # Populate response_data (as in update_order_status)
    response_data = OrderResponse.model_validate(final_order_obj).model_dump()
    if final_order_obj.driver_association:
        response_data['driver_info'] = TransportManagerResponse.model_validate(final_order_obj.driver_association).model_dump()
    if final_order_obj.vehicle:
        response_data['vehicle_info'] = VehicleResponse.model_validate(final_order_obj.vehicle).model_dump()
    if final_order_obj.transport_company:
        response_data['transport_company'] = TransportCompanyResponse.model_validate(final_order_obj.transport_company).model_dump()
    if final_order_obj.waste_records:
        response_data['waste_records'] = [WasteRecordResponse.model_validate(wr).model_dump() for wr in final_order_obj.waste_records]
    if final_order_obj.payments:
        response_data['payments'] = [PaymentResponse.model_validate(p).model_dump() for p in final_order_obj.payments]

    return response_data

# 获取所有订单
@router.get("/", response_model=List[OrderResponse])
async def read_orders(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[OrderStatus] = Query(None, alias="status", description="订单状态过滤"),
    transport_company_id_filter: Optional[int] = Query(None, description="按运输公司ID过滤"),
    driver_assoc_id_filter: Optional[int] = Query(None, description="按司机关联ID过滤 (TransportManager.id)"),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取订单列表 (支持按状态、运输公司、司机过滤)"""
    status_str = status_filter.value if status_filter else None

    if current_user.is_superuser:
        if transport_company_id_filter:
            orders = crud_order.get_by_transport_company(db, transport_company_id=transport_company_id_filter, skip=skip, limit=limit, status=status_str)
        elif driver_assoc_id_filter:
            orders = crud_order.get_by_driver(db, driver_manager_assoc_id=driver_assoc_id_filter, skip=skip, limit=limit, status=status_str)
        else:
            orders = crud_order.get_multi(db, skip=skip, limit=limit, status=status_str)
    elif current_user.role == UserRole.CUSTOMER:
        orders = crud_order.get_by_customer(
            db, customer_id=current_user.id, skip=skip, limit=limit, status=status_str
        )
    elif current_user.role == UserRole.PROPERTY:
        orders = crud_order.get_by_property_manager(
            db, manager_user_id=current_user.id, skip=skip, limit=limit, status=status_str
        )
    elif current_user.role == UserRole.TRANSPORT:
        # A transport user might be a primary manager of a company, a dispatcher, or a driver.
        # Determine their specific transport associations
        user_transport_assocs = db.query(TransportManager).filter(TransportManager.manager_id == current_user.id).all()
        if not user_transport_assocs:
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="当前运输用户未关联任何运输公司或角色。")

        # Scenario 1: User is a driver and wants to see their assigned orders
        # Check if driver_assoc_id_filter is provided and matches one of user's driver associations
        if driver_assoc_id_filter:
            is_their_driver_assoc = any(assoc.id == driver_assoc_id_filter and assoc.role == TransportRole.DRIVER for assoc in user_transport_assocs)
            if not is_their_driver_assoc:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权查看此司机的订单。")
            orders = crud_order.get_by_driver(db, driver_manager_assoc_id=driver_assoc_id_filter, skip=skip, limit=limit, status=status_str)
        # Scenario 2: User is associated with a company (e.g. dispatcher/primary) and wants to see company orders
        # Or if no specific filter, default to their primary company's orders or first associated company orders
        elif transport_company_id_filter:
            is_their_company = any(assoc.transport_company_id == transport_company_id_filter for assoc in user_transport_assocs)
            if not is_their_company:
                 raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权查看此运输公司的订单。")
            orders = crud_order.get_by_transport_company(db, transport_company_id=transport_company_id_filter, skip=skip, limit=limit, status=status_str)
        else:
            # Default: show orders for the first company they are associated with (could be refined)
            # Or if they are *only* a driver, show their orders by default.
            # For simplicity, if they are a manager/dispatcher of a company, show that company's orders.
            # If they are only a driver, show their assigned orders.
            # This logic needs to be robust based on business rules.
            # Example: Prioritize showing company orders if they manage one.
            managed_company_ids = list(set(assoc.transport_company_id for assoc in user_transport_assocs if assoc.is_primary or assoc.role == TransportRole.DISPATCHER))
            if managed_company_ids:
                 # If managing multiple, maybe require company_id_filter or show first one.
                 orders = crud_order.get_by_transport_company(db, transport_company_id=managed_company_ids[0], skip=skip, limit=limit, status=status_str)
            else: # Likely just a driver
                 driver_assocs = [assoc for assoc in user_transport_assocs if assoc.role == TransportRole.DRIVER]
                 if driver_assocs:
                     # Show orders for their first driver profile, or require driver_assoc_id_filter
                     orders = crud_order.get_by_driver(db, driver_manager_assoc_id=driver_assocs[0].id, skip=skip, limit=limit, status=status_str)
                 else:
                     orders = [] # No specific view defined for this transport user without filters

    elif current_user.role == UserRole.RECYCLING:
        orders = crud_order.get_by_recycling_manager( # This might need update to get_by_recycling_company_manager if logic changes
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
    order = db.query(Order).options(
        joinedload(Order.address).joinedload(Address.community),
        joinedload(Order.transport_company),
        joinedload(Order.driver_association).joinedload(TransportManager.manager), # Eager load driver's user details
        joinedload(Order.driver_association).joinedload(TransportManager.vehicle_assignments), # If driver has direct vehicle link
        joinedload(Order.vehicle),
        joinedload(Order.recycling_company), # Assuming RecyclingCompany relationship exists
        joinedload(Order.waste_records).joinedload(WasteRecord.recorded_by_user),
        joinedload(Order.payments)
    ).filter(Order.id == order_id).first()

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
                if pm_rec.property_company_id:
                    property_communities = db.query(Community.id).filter(Community.property_company_id == pm_rec.property_company_id).all()
                    for pc_id_tuple in property_communities:
                        accessible_communities.add(pc_id_tuple[0]) # pc_id_tuple[0] is community_id
            else:
                if pm_rec.community_id:
                    accessible_communities.add(pm_rec.community_id)
        
        if order.address.community_id not in accessible_communities:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="此订单不属于您管理的小区范围")
            
    elif current_user.role == UserRole.TRANSPORT:
        # User with TRANSPORT role can see if:
        # 1. They are the assigned dispatcher (order.transport_manager_id == current_user.id)
        # 2. They are the assigned driver (order.driver_association.manager_id == current_user.id)
        # 3. They are a primary manager or dispatcher of the order's transport_company_id
        can_view_transport = False
        if order.transport_manager_id == current_user.id: # Is dispatcher for this order
            can_view_transport = True
        if order.driver_association and order.driver_association.manager_id == current_user.id: # Is driver for this order
            can_view_transport = True
        
        if not can_view_transport and order.transport_company_id:
            # Check if current_user is a manager (primary or dispatcher) of the order's transport company
            user_company_assoc = crud_transport_manager.transport_manager.get_by_company_and_manager_user(
                db, transport_company_id=order.transport_company_id, manager_user_id=current_user.id
            )
            if user_company_assoc and (user_company_assoc.is_primary or user_company_assoc.role == TransportRole.DISPATCHER):
                can_view_transport = True
        
        if not can_view_transport:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有足够的权限查看此订单的运输信息")
            
    elif current_user.role == UserRole.RECYCLING:
        if order.recycling_company_id:
            user_rc_assoc = crud_recycling_manager.recycling_manager.get_by_company_and_manager_user(
                db, recycling_company_id=order.recycling_company_id, manager_user_id=current_user.id
            )
            if not user_rc_assoc:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您无权查看此回收公司的订单信息。")
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="订单尚未分配到回收公司。")
    else: # Other roles not explicitly handled for GET /orders/{order_id}
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您的角色无权查看此订单详情")

    # Populate driver_info and vehicle_info for the response if they exist
    response_data = OrderResponse.model_validate(order).model_dump()
    if order.driver_association:
        response_data['driver_info'] = TransportManagerResponse.model_validate(order.driver_association).model_dump()
    if order.vehicle:
        response_data['vehicle_info'] = VehicleResponse.model_validate(order.vehicle).model_dump()
    if order.transport_company:
        response_data['transport_company'] = TransportCompanyResponse.model_validate(order.transport_company).model_dump()
    if order.waste_records:
        response_data['waste_records'] = [WasteRecordResponse.model_validate(wr).model_dump() for wr in order.waste_records]
    if order.payments:
        response_data['payments'] = [PaymentResponse.model_validate(p).model_dump() for p in order.payments]
    # Add similar for recycling_company if needed in response schema explicitly
    
    return response_data

# 更新订单状态
@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    status_update: OrderStatusUpdate, # Contains new transport fields
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """更新订单状态 (now handles new transport fields)"""
    order_obj = crud_order.get(db, id=order_id)
    if not order_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
    
    current_status_str = order_obj.status # current status as string from DB
    new_status_enum = status_update.status # new status as Pydantic enum
    
    update_kwargs = status_update.model_dump(exclude_unset=True)
    update_kwargs.pop("status", None)

    can_update = False
    is_transport_role_user = current_user.role == UserRole.TRANSPORT

    if current_user.is_superuser:
        can_update = True
    elif new_status_enum == OrderStatus.PROPERTY_CONFIRMED:
        if current_user.role == UserRole.PROPERTY and current_status_str == OrderStatus.PENDING.value:
            # (Property confirm logic as before)
            can_update = True
            update_kwargs["property_manager_id"] = current_user.id
            if "property_confirm_time" not in update_kwargs or update_kwargs["property_confirm_time"] is None:
                 update_kwargs["property_confirm_time"] = datetime.datetime.utcnow()
            if not order_obj.address or not order_obj.address.community_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="订单地址或小区信息不完整，无法确认。")
            accessible_communities = set()
            pm_records = db.query(PropertyManager).filter(PropertyManager.manager_id == current_user.id).all()
            if not pm_records: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您未被指定为任何物业的管理员。")
            for pm_rec in pm_records:
                if pm_rec.is_primary and pm_rec.property_company_id:
                    communities_of_property = db.query(Community.id).filter(Community.property_company_id == pm_rec.property_company_id).all()
                    for pc_id_tuple in communities_of_property: accessible_communities.add(pc_id_tuple[0])
                elif not pm_rec.is_primary and pm_rec.community_id: accessible_communities.add(pm_rec.community_id)
            if order_obj.address.community_id not in accessible_communities:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您无权确认此小区的订单。")
        else:
            detail_msg = "只有物业管理员可以将待处理订单确认为物业已确认。"
            if current_status_str != OrderStatus.PENDING.value: detail_msg = "只能从待处理状态更改为物业确认状态。"
            if current_user.role != UserRole.PROPERTY: detail_msg = "只有物业管理员可以确认订单。"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail_msg)

    elif new_status_enum == OrderStatus.TRANSPORT_ASSIGNED:
        if is_transport_role_user and current_status_str == OrderStatus.PROPERTY_CONFIRMED.value:
            # User must be a dispatcher or primary manager of a transport company
            # The dispatcher (current_user.id) is set as transport_manager_id
            # driver_assoc_id (TransportManager.id for a driver), vehicle_id, transport_company_id must be provided in status_update
            
            if not status_update.driver_assoc_id or not status_update.vehicle_id or not status_update.transport_company_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="分配运输时，必须提供司机、车辆和运输公司信息。")

            # Validate transport_company_id
            transport_company = crud_transport_company.transport_company.get(db, id=status_update.transport_company_id)
            if not transport_company:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"运输公司 {status_update.transport_company_id} 不存在。")

            # Validate current user (dispatcher) is part of this transport_company
            dispatcher_assoc = crud_transport_manager.transport_manager.get_by_company_and_manager_user(
                db, transport_company_id=transport_company.id, manager_user_id=current_user.id
            )
            if not dispatcher_assoc or not (dispatcher_assoc.is_primary or dispatcher_assoc.role == TransportRole.DISPATCHER):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您无权为此运输公司分配订单。")

            # Validate driver_assoc_id (is a DRIVER, belongs to the SAME transport_company, and is AVAILABLE)
            driver_assoc = crud_transport_manager.transport_manager.get(db, id=status_update.driver_assoc_id)
            if not driver_assoc or driver_assoc.role != TransportRole.DRIVER:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"提供的司机ID {status_update.driver_assoc_id} 无效或不是司机角色。")
            if driver_assoc.transport_company_id != transport_company.id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"司机 {driver_assoc.manager.username if driver_assoc.manager else status_update.driver_assoc_id} 不属于运输公司 {transport_company.name}。")
            if driver_assoc.driver_status != DriverStatus.AVAILABLE: # Make sure DriverStatus is imported from models
                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"司机 {driver_assoc.manager.username if driver_assoc.manager else status_update.driver_assoc_id} 当前状态为 {driver_assoc.driver_status}, 不可用。")


            # Validate vehicle_id (belongs to the SAME transport_company, and is AVAILABLE)
            vehicle = crud_vehicle.vehicle.get(db, id=status_update.vehicle_id)
            if not vehicle:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"车辆ID {status_update.vehicle_id} 无效。")
            if vehicle.transport_company_id != transport_company.id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"车辆 {vehicle.plate_number} 不属于运输公司 {transport_company.name}。")
            if vehicle.status != VehicleStatus.AVAILABLE: # Make sure VehicleStatus is imported
                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"车辆 {vehicle.plate_number} 当前状态为 {vehicle.status}, 不可用。")

            can_update = True
            update_kwargs["transport_manager_id"] = current_user.id # The dispatcher making the assignment
            # driver_assoc_id, vehicle_id, transport_company_id are already in update_kwargs from status_update
            
            # Optionally, update driver and vehicle status to 'ON_TASK' or similar
            crud_transport_manager.transport_manager.update(db, db_obj=driver_assoc, obj_in={"driver_status": DriverStatus.ON_TASK})
            crud_vehicle.vehicle.update(db, db_obj=vehicle, obj_in={"status": VehicleStatus.ON_TASK})
        else:
            detail="只有运输调度员或主管可以将物业确认的订单分配运输。"
            if current_status_str != OrderStatus.PROPERTY_CONFIRMED.value: detail = "订单必须为物业已确认状态才能分配运输。"
            if not is_transport_role_user : detail = "您没有运输管理权限。"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    elif new_status_enum == OrderStatus.TRANSPORTING:
        if is_transport_role_user and current_status_str == OrderStatus.TRANSPORT_ASSIGNED.value:
            # User should be the assigned driver for this order, or a dispatcher/primary of the company
            is_assigned_driver = order_obj.driver_association and order_obj.driver_association.manager_id == current_user.id
            
            is_company_manager = False
            if order_obj.transport_company_id:
                actor_assoc = crud_transport_manager.transport_manager.get_by_company_and_manager_user(
                    db, transport_company_id=order_obj.transport_company_id, manager_user_id=current_user.id
                )
                if actor_assoc and (actor_assoc.is_primary or actor_assoc.role == TransportRole.DISPATCHER):
                    is_company_manager = True
            
            if not (is_assigned_driver or is_company_manager):
                 raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有订单的指定司机或公司调度/主管才能更新为运输中。")
            
            can_update = True
            if "actual_pickup_time" not in update_kwargs or update_kwargs["actual_pickup_time"] is None:
                update_kwargs["actual_pickup_time"] = datetime.datetime.utcnow()
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只有运输人员可以将已分配运输的订单更新为运输中。")

    elif new_status_enum == OrderStatus.DELIVERED:
        if is_transport_role_user and current_status_str == OrderStatus.TRANSPORTING.value:
            # Similar permission check as TRANSPORTING
            is_assigned_driver = order_obj.driver_association and order_obj.driver_association.manager_id == current_user.id
            is_company_manager = False
            if order_obj.transport_company_id:
                actor_assoc = crud_transport_manager.transport_manager.get_by_company_and_manager_user(
                    db, transport_company_id=order_obj.transport_company_id, manager_user_id=current_user.id
                )
                if actor_assoc and (actor_assoc.is_primary or actor_assoc.role == TransportRole.DISPATCHER):
                    is_company_manager = True

            if not (is_assigned_driver or is_company_manager):
                 raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有订单的指定司机或公司调度/主管才能更新为已送达。")

            can_update = True
            if "delivery_time" not in update_kwargs or update_kwargs["delivery_time"] is None:
                update_kwargs["delivery_time"] = datetime.datetime.utcnow()
            
            # After delivery, set driver and vehicle back to AVAILABLE
            if order_obj.driver_association:
                crud_transport_manager.transport_manager.update(db, db_obj=order_obj.driver_association, obj_in={"driver_status": DriverStatus.AVAILABLE})
            if order_obj.vehicle:
                crud_vehicle.vehicle.update(db, db_obj=order_obj.vehicle, obj_in={"status": VehicleStatus.AVAILABLE})
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只有运输人员可以将运输中的订单更新为已送达。")
    
    # ... (RECYCLING_CONFIRMED, COMPLETED, CANCELLED logic mostly same, ensure recycling_company_id from status_update is used if provided) ...
    elif new_status_enum == OrderStatus.RECYCLING_CONFIRMED:
        if current_user.role == UserRole.RECYCLING and current_status_str == OrderStatus.DELIVERED.value:
            if not order_obj.recycling_company_id and not status_update.recycling_company_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="回收确认时必须提供或订单已关联回收公司ID。")
            
            target_recycling_company_id = status_update.recycling_company_id or order_obj.recycling_company_id
            if not target_recycling_company_id:
                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无法确定回收公司ID进行确认。")

            rc_company = crud_recycling_company.recycling_company.get(db, id=target_recycling_company_id)
            if not rc_company:
                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"回收公司 {target_recycling_company_id} 不存在。")

            user_rc_assoc = crud_recycling_manager.recycling_manager.get_by_company_and_manager_user(
                db, recycling_company_id=rc_company.id, manager_user_id=current_user.id
            )
            # Typically, any manager (primary or specific role like supervisor/pounder) of the company can confirm.
            if not user_rc_assoc: # or check specific roles: (user_rc_assoc.is_primary or user_rc_assoc.role in [RecyclingRole.SUPERVISOR, RecyclingRole.POUNDER])
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"您不是回收公司 {rc_company.name} 的授权人员，无法确认订单。")

            can_update = True
            update_kwargs["recycling_manager_id"] = current_user.id # User making the confirmation
            update_kwargs["recycling_company_id"] = rc_company.id # Ensure it's set on the order
            if "recycling_confirm_time" not in update_kwargs or update_kwargs["recycling_confirm_time"] is None:
                update_kwargs["recycling_confirm_time"] = datetime.datetime.utcnow()
        else:
            detail_msg="只有回收站管理员可以将已送达的订单确认为回收站已确认。"
            if current_status_str != OrderStatus.DELIVERED.value: detail_msg = "订单必须为已送达状态才能进行回收确认。"
            if current_user.role != UserRole.RECYCLING: detail_msg = "只有回收站管理员有权限。"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail_msg)

    elif new_status_enum == OrderStatus.COMPLETED:
        if current_user.role == UserRole.RECYCLING and current_status_str == OrderStatus.RECYCLING_CONFIRMED.value:
            if not order_obj.recycling_company_id:
                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="订单未关联回收公司，无法完成。")
            # user_rc_assoc = db.query(RecyclingManager).filter(
            #     RecyclingManager.recycling_company_id == order_obj.recycling_company_id,
            #     RecyclingManager.manager_id == current_user.id
            # ).first()
            user_rc_assoc = crud_recycling_manager.recycling_manager.get_by_company_and_manager_user(
                db, recycling_company_id=order_obj.recycling_company_id, manager_user_id=current_user.id
            )
            # Typically, any manager (primary or supervisor) can mark as completed.
            if not user_rc_assoc: # or check specific roles: (user_rc_assoc.is_primary or user_rc_assoc.role == RecyclingRole.SUPERVISOR)
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您无权完成此回收公司的订单。")
            can_update = True
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只有回收站管理员可以将回收站确认的订单标记为完成。")

    elif new_status_enum == OrderStatus.CANCELLED:
        # (Cancellation logic as before, check roles and current_status_str)
        if current_user.role == UserRole.CUSTOMER and order_obj.customer_id == current_user.id and current_status_str == OrderStatus.PENDING.value:
            can_update = True
        elif current_user.role == UserRole.PROPERTY and current_status_str in [OrderStatus.PENDING.value, OrderStatus.PROPERTY_CONFIRMED.value]:
            # Add community access check for property manager cancelling
            # (community access check logic from property confirm)
            if not order_obj.address or not order_obj.address.community_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="订单地址或小区信息不完整，无法取消。")
            accessible_communities = set() # ... (populate accessible_communities) ...
            pm_records = db.query(PropertyManager).filter(PropertyManager.manager_id == current_user.id).all()
            if not pm_records: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您未被指定为任何物业的管理员。")
            for pm_rec in pm_records:
                if pm_rec.is_primary and pm_rec.property_company_id:
                    communities_of_property = db.query(Community.id).filter(Community.property_company_id == pm_rec.property_company_id).all()
                    for pc_id_tuple in communities_of_property: accessible_communities.add(pc_id_tuple[0])
                elif not pm_rec.is_primary and pm_rec.community_id: accessible_communities.add(pm_rec.community_id)
            if order_obj.address.community_id not in accessible_communities:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您无权取消此小区的订单。")
            can_update = True
        elif current_user.is_superuser: 
            can_update = True
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="订单状态无法取消或您无权取消。")
        
        # If order was in a transport state, revert driver/vehicle status
        if order_obj.status in [OrderStatus.TRANSPORT_ASSIGNED.value, OrderStatus.TRANSPORTING.value]:
            if order_obj.driver_association and order_obj.driver_association.driver_status == DriverStatus.ON_TASK:
                crud_transport_manager.transport_manager.update(db, db_obj=order_obj.driver_association, obj_in={"driver_status": DriverStatus.AVAILABLE})
            if order_obj.vehicle and order_obj.vehicle.status == VehicleStatus.ON_TASK:
                crud_vehicle.vehicle.update(db, db_obj=order_obj.vehicle, obj_in={"status": VehicleStatus.AVAILABLE})


    if not can_update and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您无权将订单更新到此状态或不满足状态流转条件。")

    updated_order_db = crud_order.update_status(db, db_obj=order_obj, status=new_status_enum.value, **update_kwargs)
    
    # Re-fetch with relationships for response
    # updated_order_response = await read_order(db=db, order_id=updated_order_db.id, current_user=current_user) # This creates a new dep call
    # Or, manually construct the response if performance is critical, or ensure CRUD returns with relations.
    # For simplicity and to use the same response structure:
    
    # Eager load for response
    final_order_obj = db.query(Order).options(
        joinedload(Order.address),
        joinedload(Order.transport_company),
        joinedload(Order.driver_association).joinedload(TransportManager.manager),
        joinedload(Order.vehicle),
        joinedload(Order.recycling_company),
        joinedload(Order.waste_records).joinedload(WasteRecord.recorded_by_user),
        joinedload(Order.payments)
    ).filter(Order.id == updated_order_db.id).first()

    response_data = OrderResponse.model_validate(final_order_obj).model_dump()
    if final_order_obj.driver_association:
        response_data['driver_info'] = TransportManagerResponse.model_validate(final_order_obj.driver_association).model_dump()
    if final_order_obj.vehicle:
        response_data['vehicle_info'] = VehicleResponse.model_validate(final_order_obj.vehicle).model_dump()
    if final_order_obj.transport_company:
        response_data['transport_company'] = TransportCompanyResponse.model_validate(final_order_obj.transport_company).model_dump()
    if final_order_obj.waste_records:
        response_data['waste_records'] = [WasteRecordResponse.model_validate(wr).model_dump() for wr in final_order_obj.waste_records]
    if final_order_obj.payments:
        response_data['payments'] = [PaymentResponse.model_validate(p).model_dump() for p in final_order_obj.payments]
    
    return response_data

# 更新订单信息
@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    order_in: OrderUpdate, # Contains new transport fields
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """更新订单信息 (general update, restricted by role and status)"""
    order_obj = crud_order.get(db, id=order_id)
    if not order_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")

    can_edit_fields = False
    allowed_fields = set()
    update_data_dict = order_in.model_dump(exclude_unset=True)

    if current_user.is_superuser:
        can_edit_fields = True
        allowed_fields = set(update_data_dict.keys()) # Superuser can edit all provided fields
    elif current_user.role == UserRole.CUSTOMER:
        if order_obj.customer_id == current_user.id and order_obj.status == OrderStatus.PENDING.value:
            can_edit_fields = True
            allowed_fields = {"address_id", "waste_type", "waste_volume", "expected_pickup_time", "notes"} # Customer editable fields
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只能更新自己且状态为待处理的订单。")
    elif current_user.role == UserRole.PROPERTY:
        # (Property permission check logic as before)
        if order_obj.status in [OrderStatus.PENDING.value, OrderStatus.PROPERTY_CONFIRMED.value]:
            # (Community access check logic ...)
            can_edit_fields = True
            allowed_fields = {"property_notes"} # Property manager editable fields
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="物业只能更新待处理或物业已确认状态的订单。")
    elif current_user.role == UserRole.TRANSPORT:
        # Dispatcher/Primary manager of the order's transport company can edit transport specific fields
        # if order_obj.transport_company_id:
        #     actor_assoc = crud_transport_manager.transport_manager.get_by_company_and_manager_user(
        #         db, transport_company_id=order_obj.transport_company_id, manager_user_id=current_user.id
        #     )
        #     if actor_assoc and (actor_assoc.is_primary or actor_assoc.role == TransportRole.DISPATCHER):
        #         if order_obj.status in [OrderStatus.PROPERTY_CONFIRMED.value, OrderStatus.TRANSPORT_ASSIGNED.value]:
        #             can_edit_fields = True
        #             allowed_fields = {"transport_notes", "driver_assoc_id", "vehicle_id", "transport_route", "transport_company_id"}
        #                 # Be careful: changing driver/vehicle here vs. dedicated status update endpoint.
        #                 # This general update might be for correcting details rather than operational changes.
        # if not can_edit_fields:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="运输人员通常通过状态更新来修改运输相关信息，或权限不足。")

    # Check if trying to update disallowed fields
    for field_key in update_data_dict.keys():
        if field_key not in allowed_fields and not current_user.is_superuser: # Superuser bypasses this check
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"您的角色无权更新字段 '{field_key}'.")

    if not can_edit_fields: # Should be caught by specific role checks above, but as a fallback
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您无权修改此订单的这些字段或当前状态不允许修改。")

    updated_order_db = crud_order.update(db, db_obj=order_obj, obj_in=order_in) # obj_in here is OrderUpdate schema
    
    final_order_obj = db.query(Order).options(
        joinedload(Order.address),
        joinedload(Order.transport_company),
        joinedload(Order.driver_association).joinedload(TransportManager.manager),
        joinedload(Order.vehicle),
        joinedload(Order.recycling_company),
        joinedload(Order.waste_records).joinedload(WasteRecord.recorded_by_user),
        joinedload(Order.payments)
    ).filter(Order.id == updated_order_db.id).first()

    response_data = OrderResponse.model_validate(final_order_obj).model_dump()
    if final_order_obj.driver_association:
        response_data['driver_info'] = TransportManagerResponse.model_validate(final_order_obj.driver_association).model_dump()
    if final_order_obj.vehicle:
        response_data['vehicle_info'] = VehicleResponse.model_validate(final_order_obj.vehicle).model_dump()
    if final_order_obj.transport_company:
        response_data['transport_company'] = TransportCompanyResponse.model_validate(final_order_obj.transport_company).model_dump()
    if final_order_obj.waste_records:
        response_data['waste_records'] = [WasteRecordResponse.model_validate(wr).model_dump() for wr in final_order_obj.waste_records]
    if final_order_obj.payments:
        response_data['payments'] = [PaymentResponse.model_validate(p).model_dump() for p in final_order_obj.payments]
    return response_data

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
        if order_obj.customer_id == current_user.id and order_obj.status == OrderStatus.PENDING.value:
            can_delete = True
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="客户只能删除自己且状态为待处理的订单。")
    # Add logic if property managers can delete orders from their communities (with community check)
    # Add logic if transport managers can delete (e.g. if not yet picked up)

    if not can_delete:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您无权删除此订单。")
    
    # If order was in a transport state, revert driver/vehicle status
    if order_obj.status in [OrderStatus.TRANSPORT_ASSIGNED.value, OrderStatus.TRANSPORTING.value]:
        if order_obj.driver_association and order_obj.driver_association.driver_status == DriverStatus.ON_TASK:
            crud_transport_manager.transport_manager.update(db, db_obj=order_obj.driver_association, obj_in={"driver_status": DriverStatus.AVAILABLE})
        if order_obj.vehicle and order_obj.vehicle.status == VehicleStatus.ON_TASK:
            crud_vehicle.vehicle.update(db, db_obj=order_obj.vehicle, obj_in={"status": VehicleStatus.AVAILABLE})

    deleted_order = crud_order.remove(db, id=order_id)
    # For response, it might be better to return a simple success message or the ID,
    # as the full object with relationships might fail if cascade deletes are aggressive.
    # However, the model still expects OrderResponse.
    return deleted_order # This might fail if relations are gone.
                         # Consider returning a simple dict or status code only.