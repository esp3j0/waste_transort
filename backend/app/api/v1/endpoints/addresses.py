from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
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
    addresses_db = crud.address.get_multi_by_user(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    return [schemas.AddressResponse.model_validate(addr).model_dump() for addr in addresses_db]

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
    address_db = crud.address.create_with_user(
        db=db, obj_in=address_in, user_id=current_user.id
    )
    return schemas.AddressResponse.model_validate(address_db).model_dump()

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
    address_db = crud.address.get(db=db, id=address_id)
    if not address_db:
        raise HTTPException(status_code=404, detail="地址不存在")
    if address_db.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="没有足够的权限")
    updated_address_db = crud.address.update(db=db, db_obj=address_db, obj_in=address_in)
    return schemas.AddressResponse.model_validate(updated_address_db).model_dump()

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
    address_db = crud.address.get(db=db, id=address_id)
    if not address_db:
        raise HTTPException(status_code=404, detail="地址不存在")
    if address_db.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="没有足够的权限")
    return schemas.AddressResponse.model_validate(address_db).model_dump()

@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(
    *,
    db: Session = Depends(deps.get_db),
    address_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> None:
    """
    删除地址
    """
    address_db = crud.address.get(db=db, id=address_id)
    if not address_db:
        raise HTTPException(status_code=404, detail="地址不存在")
    if address_db.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="没有足够的权限")
        
    crud.address.remove(db=db, id=address_id)
    return

@router.get("/default", response_model=schemas.AddressResponse)
def read_default_address(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    获取默认地址
    """
    address_db = crud.address.get_default_address(db=db, user_id=current_user.id)
    if not address_db:
        raise HTTPException(status_code=404, detail="默认地址不存在")
    return schemas.AddressResponse.model_validate(address_db).model_dump()

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
    address_db = crud.address.get(db=db, id=address_id)
    if not address_db:
        raise HTTPException(status_code=404, detail="地址不存在")
    if address_db.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="没有足够的权限")
    updated_address_db = crud.address.set_default_address(
        db=db, address_id=address_id, user_id=current_user.id
    )
    return schemas.AddressResponse.model_validate(updated_address_db).model_dump() 