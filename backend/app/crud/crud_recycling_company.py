from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.models.recycling_company import RecyclingCompany, RecyclingCompanyStatus, RecyclingCompanyType
from app.models.recycling_manager import RecyclingManager
from app.schemas.recycling_company import RecyclingCompanyCreate, RecyclingCompanyUpdate, RecyclingCompanyStatusUpdate

class CRUDRecyclingCompany(CRUDBase[RecyclingCompany, RecyclingCompanyCreate, RecyclingCompanyUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[RecyclingCompany]:
        """根据回收公司名称获取信息"""
        return db.query(RecyclingCompany).filter(RecyclingCompany.name == name).first()
    
    def get_by_company_type(
        self, db: Session, *, company_type: RecyclingCompanyType, skip: int = 0, limit: int = 100
    ) -> List[RecyclingCompany]:
        """根据回收公司类型获取信息"""
        return db.query(RecyclingCompany).filter(RecyclingCompany.company_type == company_type).offset(skip).limit(limit).all()
    
    def get_by_status(
        self, db: Session, *, status: RecyclingCompanyStatus, skip: int = 0, limit: int = 100
    ) -> List[RecyclingCompany]:
        """根据回收公司运营状态获取信息"""
        return db.query(RecyclingCompany).filter(RecyclingCompany.status == status).offset(skip).limit(limit).all()
    
    # get_by_manager 将在 crud_recycling_manager.py 中实现，因为 manager 是关联到 RecyclingManager
    # 但如果需要通过公司查找其主要管理员管理的公司，可以在这里添加，或者通过 RecyclingManager 反查

    def get_active_companies(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[RecyclingCompany]:
        """获取所有正常运营的回收公司"""
        return db.query(RecyclingCompany).filter(
            RecyclingCompany.status == RecyclingCompanyStatus.ACTIVE,
            RecyclingCompany.is_active == True
        ).offset(skip).limit(limit).all()
    
    def update_company_status(self, db: Session, *, db_obj: RecyclingCompany, status_in: RecyclingCompanyStatusUpdate) -> RecyclingCompany:
        """更新回收公司运营状态和可选的当前负载"""
        update_data = status_in.model_dump(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def update_current_load(self, db: Session, *, db_obj: RecyclingCompany, additional_load: float) -> RecyclingCompany:
        """更新回收公司当前负载 (增加或减少)"""
        # Ensure current_load_tons is not None before operation
        current_load = db_obj.current_load_tons if db_obj.current_load_tons is not None else 0.0
        new_load = current_load + additional_load
        return super().update(db, db_obj=db_obj, obj_in={"current_load_tons": new_load})
    
    def create_with_primary_manager(self, db: Session, *, obj_in: RecyclingCompanyCreate, primary_manager_user_id: int) -> RecyclingCompany:
        """创建回收公司并自动设置一个主要管理员。"""
        db_company = super().create(db, obj_in=obj_in)
        # 创建 RecyclingManager 记录
        # 假设 RecyclingManagerCreate schema 和 CRUD 操作已准备好
        # 这里直接创建 RecyclingManager 对象，理想情况下应通过其 CRUD 进行
        manager_assoc = RecyclingManager(
            recycling_company_id=db_company.id,
            manager_id=primary_manager_user_id,
            is_primary=True,
            role=None # 主要管理员 role 为 None
        )
        db.add(manager_assoc)
        db.commit()
        db.refresh(db_company) # 刷新以包含关系
        return db_company

    def get_by_manager_user(
        self, db: Session, *, manager_user_id: int, skip: int = 0, limit: int = 100
    ) -> List[RecyclingCompany]:
        """获取用户管理的所有回收公司。"""
        return (
            db.query(self.model)
            .join(RecyclingManager, self.model.id == RecyclingManager.recycling_company_id)
            .filter(RecyclingManager.manager_id == manager_user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

recycling_company = CRUDRecyclingCompany(RecyclingCompany)
