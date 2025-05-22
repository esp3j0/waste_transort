from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.AddressResponse])
def read_addresses(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    获取当前用户的所有地址
    """
    addresses = crud.address.get_multi_by_user(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    return addresses

@router.post("/", response_model=schemas.AddressResponse)
def create_address(
    *,
    db: Session = Depends(deps.get_db),
    address_in: schemas.AddressCreate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    创建新地址
    """
    address = crud.address.create_with_user(
        db=db, obj_in=address_in, user_id=current_user.id
    )
    return address

@router.put("/{address_id}", response_model=schemas.AddressResponse)
def update_address(
    *,
    db: Session = Depends(deps.get_db),
    address_id: int,
    address_in: schemas.AddressUpdate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    更新地址
    """
    address = crud.address.get(db=db, id=address_id)
    if not address:
        raise HTTPException(status_code=404, detail="地址不存在")
    if address.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="没有足够的权限")
    address = crud.address.update(db=db, db_obj=address, obj_in=address_in)
    return address

@router.get("/{address_id}", response_model=schemas.AddressResponse)
def read_address(
    *,
    db: Session = Depends(deps.get_db),
    address_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    获取指定地址
    """
    address = crud.address.get(db=db, id=address_id)
    if not address:
        raise HTTPException(status_code=404, detail="地址不存在")
    if address.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="没有足够的权限")
    return address

@router.delete("/{address_id}", response_model=schemas.AddressResponse)
def delete_address(
    *,
    db: Session = Depends(deps.get_db),
    address_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    删除地址
    """
    address = crud.address.get(db=db, id=address_id)
    if not address:
        raise HTTPException(status_code=404, detail="地址不存在")
    if address.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="没有足够的权限")
    address = crud.address.remove(db=db, id=address_id)
    return address

@router.get("/default", response_model=schemas.AddressResponse)
def read_default_address(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    获取默认地址
    """
    address = crud.address.get_default_address(db=db, user_id=current_user.id)
    if not address:
        raise HTTPException(status_code=404, detail="默认地址不存在")
    return address

@router.post("/{address_id}/set-default", response_model=schemas.AddressResponse)
def set_default_address(
    *,
    db: Session = Depends(deps.get_db),
    address_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    设置默认地址
    """
    address = crud.address.get(db=db, id=address_id)
    if not address:
        raise HTTPException(status_code=404, detail="地址不存在")
    if address.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="没有足够的权限")
    address = crud.address.set_default_address(
        db=db, address_id=address_id, user_id=current_user.id
    )
    return address 