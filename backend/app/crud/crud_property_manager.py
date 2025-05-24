from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.crud.base import CRUDBase
from app.models.property_manager import PropertyManager
from app.schemas.property_manager import PropertyManagerCreate, PropertyManagerUpdate

class CRUDPropertyManager(CRUDBase[PropertyManager, PropertyManagerCreate, PropertyManagerUpdate]):
    def create(self, db: Session, *, obj_in: PropertyManagerCreate, property_id: int) -> PropertyManager:
        """
        创建新的物业管理员关联记录
        - property_id: 物业公司的ID，将从路径参数或依赖项中获取
        """
        if obj_in.is_primary is False and obj_in.community_id is None:
            raise HTTPException(
                status_code=400,
                detail="非主要管理员必须关联一个小区 (community_id is required for non-primary managers)."
            )
        if obj_in.is_primary is True and obj_in.community_id is not None:
            # 根据需求，如果主要管理员不应关联小区，则取消下面的注释或将community_id设为None
            # raise HTTPException(
            #     status_code=400,
            #     detail="主要管理员不能关联特定小区，community_id 必须为 null."
            # )
            # 或者自动设置 community_id 为 None
            obj_in.community_id = None


        db_obj = PropertyManager(
            **obj_in.model_dump(),
            property_id=property_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: PropertyManager, obj_in: Union[PropertyManagerUpdate, Dict[str, Any]]
    ) -> PropertyManager:
        """
        更新物业管理员信息
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        # 确定最终的 is_primary 状态
        # 如果 is_primary 在 update_data 中，则使用新值；否则，使用 db_obj 中的旧值。
        is_primary_final = update_data.get("is_primary", db_obj.is_primary)
        
        # 确定最终的 community_id
        # 如果 community_id 在 update_data 中，则使用新值；否则，使用 db_obj 中的旧值。
        community_id_final = update_data.get("community_id", db_obj.community_id)

        if is_primary_final is False and community_id_final is None:
            raise HTTPException(
                status_code=400,
                detail="非主要管理员必须关联一个小区 (community_id cannot be null for non-primary managers when updating)."
            )

        if is_primary_final is True:
            # 如果更新后成为主要管理员，则其 community_id 应设为 None
            # 确保将 None 显式写入 update_data，以便 super().update 会应用它
            update_data["community_id"] = None
        
        # 调用父类的 update 方法前，确保 obj_in 是符合预期的类型
        # 如果原始 obj_in 是 PropertyManagerUpdate schema，并且我们修改了 update_data 字典，
        # 父类 update 可能期望的是字典或 schema 对象。
        # CRUDBase 通常处理字典形式的 update_data。
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def get_by_property_and_manager(
        self, db: Session, *, property_id: int, manager_id: int
    ) -> Optional[PropertyManager]:
        return db.query(PropertyManager).filter(
            PropertyManager.property_id == property_id,
            PropertyManager.manager_id == manager_id
        ).first()

    # 可以根据需要添加更多 specific 的查询方法
    # 例如：get_all_by_property_id, get_all_by_community_id 等

property_manager = CRUDPropertyManager(PropertyManager) 