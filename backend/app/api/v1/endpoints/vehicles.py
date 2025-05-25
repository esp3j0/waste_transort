from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.transport_company import TransportCompany
from app.models.vehicle import Vehicle, VehicleStatus
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleResponse
from app.crud import crud_vehicle, crud_transport_company, crud_transport_manager

router = APIRouter()

# Typically prefixed like /transport-companies/{company_id}/vehicles

@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
async def create_vehicle_for_company(
    *,
    db: Session = Depends(get_db),
    vehicle_in: VehicleCreate, # Contains transport_company_id
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """为运输公司添加新车辆。"""
    company = crud_transport_company.transport_company.get(db, id=vehicle_in.transport_company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transport company {vehicle_in.transport_company_id} not found.")

    # Permissions: Superuser or primary manager of the company can add vehicles
    can_add_vehicle = False
    if current_user.is_superuser:
        can_add_vehicle = True
    else:
        manager_assoc = crud_transport_manager.transport_manager.get_by_company_and_manager_user(
            db, transport_company_id=vehicle_in.transport_company_id, manager_user_id=current_user.id
        )
        if manager_assoc and manager_assoc.is_primary:
            can_add_vehicle = True
            
    if not can_add_vehicle:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add vehicles to this company.")

    existing_vehicle = crud_vehicle.vehicle.get_by_plate_number(db, plate_number=vehicle_in.plate_number)
    if existing_vehicle:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Vehicle with plate number {vehicle_in.plate_number} already exists.")
    
    # The transport_company_id is part of VehicleCreate schema
    new_vehicle = crud_vehicle.vehicle.create(db, obj_in=vehicle_in)
    return new_vehicle

@router.get("/company/{company_id}", response_model=List[VehicleResponse])
async def list_vehicles_for_company(
    *,
    db: Session = Depends(get_db),
    company_id: int,
    status_filter: Optional[VehicleStatus] = None,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取指定运输公司的车辆列表。"""
    company = crud_transport_company.transport_company.get(db, id=company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transport company {company_id} not found.")

    # Permissions: Superuser or any manager of this company
    can_view_vehicles = False
    if current_user.is_superuser:
        can_view_vehicles = True
    else:
        manager_assoc = crud_transport_manager.transport_manager.get_by_company_and_manager_user(
            db, transport_company_id=company_id, manager_user_id=current_user.id
        )
        if manager_assoc:
            can_view_vehicles = True
    
    if not can_view_vehicles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view vehicles for this company.")

    if status_filter:
        vehicles = crud_vehicle.vehicle.get_vehicles_by_status(db, transport_company_id=company_id, status=status_filter)
    else:
        vehicles = crud_vehicle.vehicle.get_by_transport_company(db, transport_company_id=company_id)
    return vehicles

@router.get("/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle_details(
    *,
    db: Session = Depends(get_db),
    vehicle_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """获取特定车辆的详细信息。"""
    db_vehicle = crud_vehicle.vehicle.get(db, id=vehicle_id)
    if not db_vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")

    # Permissions: Superuser or any manager of the vehicle's company
    can_view_vehicle = False
    if current_user.is_superuser:
        can_view_vehicle = True
    else:
        manager_assoc = crud_transport_manager.transport_manager.get_by_company_and_manager_user(
            db, transport_company_id=db_vehicle.transport_company_id, manager_user_id=current_user.id
        )
        if manager_assoc:
            can_view_vehicle = True
    
    if not can_view_vehicle:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this vehicle.")
    return db_vehicle

@router.put("/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle_details(
    *,
    db: Session = Depends(get_db),
    vehicle_id: int,
    vehicle_in: VehicleUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """更新车辆信息。"""
    db_vehicle = crud_vehicle.vehicle.get(db, id=vehicle_id)
    if not db_vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")

    # Permissions: Superuser or primary manager of the vehicle's company
    can_update_vehicle = False
    if current_user.is_superuser:
        can_update_vehicle = True
    else:
        manager_assoc = crud_transport_manager.transport_manager.get_by_company_and_manager_user(
            db, transport_company_id=db_vehicle.transport_company_id, manager_user_id=current_user.id
        )
        if manager_assoc and manager_assoc.is_primary:
            can_update_vehicle = True
            
    if not can_update_vehicle:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this vehicle.")
    
    # If plate_number is being changed, check for uniqueness again
    if vehicle_in.plate_number and vehicle_in.plate_number != db_vehicle.plate_number:
        existing_vehicle = crud_vehicle.vehicle.get_by_plate_number(db, plate_number=vehicle_in.plate_number)
        if existing_vehicle and existing_vehicle.id != vehicle_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Another vehicle with plate number {vehicle_in.plate_number} already exists.")

    updated_vehicle = crud_vehicle.vehicle.update(db, db_obj=db_vehicle, obj_in=vehicle_in)
    return updated_vehicle

@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(
    *,
    db: Session = Depends(get_db),
    vehicle_id: int,
    current_user: User = Depends(get_current_active_user)
) -> None:
    """从系统中删除车辆。"""
    db_vehicle = crud_vehicle.vehicle.get(db, id=vehicle_id)
    if not db_vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")

    # Permissions: Superuser or primary manager of the vehicle's company
    can_delete_vehicle = False
    if current_user.is_superuser:
        can_delete_vehicle = True
    else:
        manager_assoc = crud_transport_manager.transport_manager.get_by_company_and_manager_user(
            db, transport_company_id=db_vehicle.transport_company_id, manager_user_id=current_user.id
        )
        if manager_assoc and manager_assoc.is_primary:
            can_delete_vehicle = True
            
    if not can_delete_vehicle:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this vehicle.")
    
    # Consider if vehicle is in use by an order. Prevent deletion or handle gracefully.
    crud_vehicle.vehicle.remove(db, id=vehicle_id)
    return 