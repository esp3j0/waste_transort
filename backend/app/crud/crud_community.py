from typing import List, Optional
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.community import Community
from app.schemas.community import CommunityCreate, CommunityUpdate

class CRUDCommunity(CRUDBase[Community, CommunityCreate, CommunityUpdate]):
    """社区CRUD操作"""
    
    def create_with_property_company(
        self, db: Session, *, obj_in: CommunityCreate
    ) -> Community:
        """创建社区并关联物业公司"""
        return super().create(db=db, obj_in=obj_in)
    
    def get_by_property_company(
        self, db: Session, *, property_company_id: int, skip: int = 0, limit: int = 100
    ) -> List[Community]:
        """获取指定物业公司下的所有社区"""
        return db.query(Community).filter(Community.property_company_id == property_company_id).offset(skip).limit(limit).all()
    
    def get_active_communities(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Community]:
        """获取所有激活的社区"""
        return db.query(Community).filter(Community.is_active == True).offset(skip).limit(limit).all()
    
    def get_by_name(
        self, db: Session, *, name: str
    ) -> Optional[Community]:
        """根据名称获取社区"""
        return db.query(Community).filter(Community.name == name).first()
    
    def update_status(
        self, db: Session, *, db_obj: Community, is_active: bool
    ) -> Community:
        """更新社区状态"""
        db_obj.is_active = is_active
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_multi_by_property_company(
        self, db: Session, *, property_company_id: int, skip: int = 0, limit: int = 100
    ) -> List[Community]:
        """获取指定物业公司下的所有社区（分页）"""
        return (
            db.query(self.model)
            .filter(Community.property_company_id == property_company_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

community = CRUDCommunity(Community)