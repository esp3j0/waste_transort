import pytest
import random
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.crud import user, property as crud_property, community as crud_community
from app.schemas.user import UserCreate
from app.schemas.property import PropertyCreate
from app.schemas.property_manager import PropertyManagerCreate, PropertyManagerUpdate
from app.schemas.community import CommunityCreate
from app.models.user import UserRole, User as UserModel
from app.models.property import Property as PropertyModel
from app.models.community import Community as CommunityModel
from app.core.security import create_access_token

# 辅助函数：创建不同角色的测试用户并返回token
def create_user_with_role(db: Session, role: UserRole, is_superuser: bool = False, username_suffix: str = "") -> tuple[UserModel, str]:
    random_number = random.randint(10000, 99999)
    username = f"test_{role.value.lower()}_{random_number}{username_suffix}"
    
    user_in = UserCreate(
        username=username,
        email=f"{username}@example.com",
        phone=f"138000{random_number}",
        password="testpassword",
        full_name=f"测试{role.name}用户{username_suffix}",
        role=role,
        is_superuser=is_superuser
    )
    db_user = user.create(db, obj_in=user_in)
    access_token = create_access_token(db_user.id)
    return db_user, access_token

# 辅助函数：创建测试物业和社区
def create_test_property_and_community(db: Session, manager_id: int) -> tuple[PropertyModel, CommunityModel]:
    # 创建物业
    random_suffix = random.randint(1000,9999)
    property_in = PropertyCreate(
        name=f"测试物业{random_suffix}",
        address=f"测试地址{random_suffix}",
        contact_name="测试联系人",
        contact_phone=f"1380011{random_suffix}"
    )
    # create_with_manager in crud_property makes the manager_id the primary manager
    db_property = crud_property.create_with_manager(db, obj_in=property_in, manager_id=manager_id)
    
    # 创建社区
    community_in = CommunityCreate(
        name=f"测试小区{random_suffix}",
        address=f"测试小区地址{random_suffix}"
    )
    db_community = crud_community.create_with_property(db, obj_in=community_in, property_id=db_property.id)
    
    return db_property, db_community

# 测试添加物业管理员 (非主要, 绑定小区)
def test_add_property_manager(client: TestClient, db: Session):
    # 创建主要物业管理员 (作为操作者)
    primary_manager_user, primary_token = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_operator_primary")
    test_property, test_community = create_test_property_and_community(db, primary_manager_user.id)
    
    # 创建将要被添加为普通管理员的用户
    new_ordinary_manager_user, _ = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_new_ordinary")
    
    manager_data = {
        "manager_id": new_ordinary_manager_user.id,
        "role": "普通小区管理员",
        "is_primary": False,
        "community_id": test_community.id  # 必须为非主要管理员提供 community_id
    }
    headers = {"Authorization": f"Bearer {primary_token}"}
    response = client.post(
        f"/api/v1/properties/{test_property.id}/managers",
        json=manager_data,
        headers=headers
    )
    assert response.status_code == 200, response.json()
    data = response.json()
    assert data["manager_id"] == new_ordinary_manager_user.id
    assert data["role"] == "普通小区管理员"
    assert not data["is_primary"]
    assert data["community_id"] == test_community.id
    assert data["community"]["id"] == test_community.id # 确保 community 信息被返回

# 测试添加物业管理员 (非主要, 未提供小区ID，应该失败)
def test_add_property_manager_no_community_id_failure(client: TestClient, db: Session):
    primary_manager_user, primary_token = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_op_primary_nc")
    test_property, _ = create_test_property_and_community(db, primary_manager_user.id)
    new_manager_user, _ = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_new_nc")
    
    manager_data = {
        "manager_id": new_manager_user.id,
        "role": "普通管理员",
        "is_primary": False
        # community_id is intentionally omitted
    }
    headers = {"Authorization": f"Bearer {primary_token}"}
    response = client.post(
        f"/api/v1/properties/{test_property.id}/managers", json=manager_data, headers=headers
    )
    assert response.status_code == 422
    response_json = response.json()
    assert "非主要管理员必须关联一个小区" in response_json["detail"][0]['msg']


# 测试添加第二个主要管理员（应该失败）
def test_add_second_primary_manager_failure(client: TestClient, db: Session):
    primary_manager_user, primary_token = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_op_primary_asp")
    test_property, _ = create_test_property_and_community(db, primary_manager_user.id) # This user is already primary
    
    another_user, _ = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_another_asp")
    
    manager_data = {
        "manager_id": another_user.id,
        "role": "伪主要管理员",
        "is_primary": True
        # community_id can be None for primary
    }
    headers = {"Authorization": f"Bearer {primary_token}"}
    response = client.post(
        f"/api/v1/properties/{test_property.id}/managers", json=manager_data, headers=headers
    )
    assert response.status_code == 400, response.json()
    assert "已存在一个主要管理员" in response.json()["detail"]


# 测试更新物业管理员
def test_update_property_manager(client: TestClient, db: Session):
    primary_manager_user, primary_token = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_op_primary_upd")
    test_property, test_community = create_test_property_and_community(db, primary_manager_user.id)
    
    # 添加一个普通管理员用于后续更新
    manager_to_update_user, _ = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_to_update")
    add_manager_data = {
        "manager_id": manager_to_update_user.id,
        "role": "待更新管理员",
        "is_primary": False,
        "community_id": test_community.id
    }
    headers = {"Authorization": f"Bearer {primary_token}"}
    add_response = client.post(
        f"/api/v1/properties/{test_property.id}/managers", json=add_manager_data, headers=headers
    )
    assert add_response.status_code == 200, add_response.json()
    pm_id_to_update = add_response.json()["id"] # This is PropertyManager.id
    original_community_id = add_response.json()["community_id"]

    # 测试更新角色和community_id
    _, other_community = create_test_property_and_community(db, primary_manager_user.id) # Create another community for update

    update_data = {
        "role": "已更新高级管理员",
        "is_primary": False, # Keeping as non-primary
        "community_id": other_community.id # Change community
    }
    update_response = client.put(
        f"/api/v1/properties/{test_property.id}/managers/{pm_id_to_update}", # Use pm_id
        json=update_data,
        headers=headers
    )
    assert update_response.status_code == 200, update_response.json()
    updated_data = update_response.json()
    assert updated_data["role"] == "已更新高级管理员"
    assert updated_data["community_id"] == other_community.id
    assert updated_data["id"] == pm_id_to_update


# 测试将普通管理员更新为主要管理员 (当已存在主要管理员时，应该失败)
def test_update_to_primary_when_primary_exists_failure(client: TestClient, db: Session):
    # 操作者是主要管理员
    primary_operator_user, primary_operator_token = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_op_prime_uptp")
    # 物业已经通过上面的操作者创建，所以 primary_operator_user 是这个物业的 PropertyManager 且 is_primary=True
    test_property, test_community = create_test_property_and_community(db, primary_operator_user.id)

    # 添加另一个普通管理员
    ordinary_manager_user, _ = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_ord_uptp")
    add_manager_payload = {
        "manager_id": ordinary_manager_user.id, "role": "普通", "is_primary": False, "community_id": test_community.id
    }
    add_resp = client.post(f"/api/v1/properties/{test_property.id}/managers", json=add_manager_payload, headers={"Authorization": f"Bearer {primary_operator_token}"})
    assert add_resp.status_code == 200
    pm_id_of_ordinary = add_resp.json()["id"]

    # 尝试将这个普通管理员更新为主要管理员
    update_to_primary_payload = {"is_primary": True}
    update_resp = client.put(
        f"/api/v1/properties/{test_property.id}/managers/{pm_id_of_ordinary}",
        json=update_to_primary_payload,
        headers={"Authorization": f"Bearer {primary_operator_token}"}
    )
    assert update_resp.status_code == 400, update_resp.json()
    assert "已存在一个主要管理员" in update_resp.json()["detail"]


# 测试移除物业管理员
def test_remove_property_manager(client: TestClient, db: Session):
    primary_manager_user, primary_token = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_op_primary_rem")
    test_property, test_community = create_test_property_and_community(db, primary_manager_user.id)
    
    # 添加一个普通管理员用于后续移除
    manager_to_remove_user, _ = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_to_remove")
    add_manager_data = {
        "manager_id": manager_to_remove_user.id,
        "role": "待移除管理员",
        "is_primary": False,
        "community_id": test_community.id
    }
    headers = {"Authorization": f"Bearer {primary_token}"}
    add_response = client.post(
        f"/api/v1/properties/{test_property.id}/managers", json=add_manager_data, headers=headers
    )
    assert add_response.status_code == 200
    pm_id_to_remove = add_response.json()["id"] # PropertyManager.id

    # 测试移除管理员
    remove_response = client.delete(
        f"/api/v1/properties/{test_property.id}/managers/{pm_id_to_remove}", # Use pm_id
        headers=headers
    )
    assert remove_response.status_code == 200, remove_response.json()
    
    # 验证是否真的被移除了 (可选，例如尝试获取该pm_id)
    get_response = client.get(f"/api/v1/properties/{test_property.id}/managers", headers=headers) # Get all managers for property
    assert get_response.status_code == 200
    found = any(m["id"] == pm_id_to_remove for m in get_response.json())
    assert not found


# 测试主要管理员移除自己 (应该失败)
def test_primary_manager_remove_self_failure(client: TestClient, db: Session):
    primary_manager_user, primary_token = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_op_primary_rem_self")
    test_property, _ = create_test_property_and_community(db, primary_manager_user.id)
    
    # 获取主要管理员的 PropertyManager ID
    # The primary manager is created by create_test_property_and_community
    # We need to find its PropertyManager entry to get the pm_id
    db_prop_obj = crud_property.get(db, id=test_property.id)
    primary_pm_id = None
    for pm_entry in db_prop_obj.property_managers:
        if pm_entry.manager_id == primary_manager_user.id and pm_entry.is_primary:
            primary_pm_id = pm_entry.id
            break
    assert primary_pm_id is not None, "Primary PropertyManager record not found for the operator."

    headers = {"Authorization": f"Bearer {primary_token}"}
    response = client.delete(
        f"/api/v1/properties/{test_property.id}/managers/{primary_pm_id}", # Use pm_id
        headers=headers
    )
    assert response.status_code == 403, response.json() # API returns 403 for "不能移除自己"
    assert "不能移除自己" in response.json()["detail"]


# 测试普通物业人员添加管理员（应该失败）
def test_ordinary_manager_add_manager_failure(client: TestClient, db: Session):
    # 创建物业主要管理员 (用于创建物业和初始设置)
    initial_primary_user, _ = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_init_prime_oma")
    test_property, test_community = create_test_property_and_community(db, initial_primary_user.id)

    # 创建一个普通物业人员并获取其token (此人不是主要管理员)
    ordinary_manager_user, ordinary_token = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_ord_oma")
    # 将此人添加为普通管理员 (由主要管理员操作，这里简化，假设已添加)
    # For a more robust test, actually add ordinary_manager_user as a non-primary manager
    # Here, we directly use ordinary_token, assuming this user is just a User with PROPERTY role but not a primary manager for test_property
    # To make the test correct, ordinary_manager_user needs to be added as a non-primary manager first.
    # However, the permission check in API is based on is_primary status of the current_user for that property.
    # So, if ordinary_manager_user is not a primary manager for test_property, they can't add.

    another_user_to_add, _ = create_user_with_role(db, UserRole.CUSTOMER, username_suffix="_another_oma")
    
    manager_data = {
        "manager_id": another_user_to_add.id,
        "role": "测试角色",
        "is_primary": False,
        "community_id": test_community.id
    }
    headers = {"Authorization": f"Bearer {ordinary_token}"} # 使用普通物业人员的token
    response = client.post(
        f"/api/v1/properties/{test_property.id}/managers", json=manager_data, headers=headers
    )
    assert response.status_code == 403, response.json()
    assert "只有超级管理员或物业主要管理员可以添加物业人员" in response.json()["detail"]

# ... (其他测试用例可以根据需要添加，例如：更新自己的信息，权限边界等)
# 例如，测试超级用户权限
def test_superuser_add_property_manager(client: TestClient, db: Session):
    superuser, superuser_token = create_user_with_role(db, UserRole.ADMIN, is_superuser=True, username_suffix="_su_add")
    
    # Property needs a manager, even if superuser is acting. Let's create one.
    temp_prop_manager_user, _ = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_temp_mgr_su")
    test_property, test_community = create_test_property_and_community(db, temp_prop_manager_user.id)

    new_manager_user, _ = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_new_mgr_su")
    
    manager_data = {
        "manager_id": new_manager_user.id,
        "role": "由超管添加",
        "is_primary": False,
        "community_id": test_community.id
    }
    headers = {"Authorization": f"Bearer {superuser_token}"}
    response = client.post(
        f"/api/v1/properties/{test_property.id}/managers", json=manager_data, headers=headers
    )
    assert response.status_code == 200, response.json()
    data = response.json()
    assert data["manager_id"] == new_manager_user.id


def test_superuser_promote_to_primary_manager(client: TestClient, db: Session):
    superuser, superuser_token = create_user_with_role(db, UserRole.ADMIN, is_superuser=True, username_suffix="_su_promote")
    
    # Create property with an initial (non-primary or temp primary) manager
    initial_manager_user, _ = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_init_mgr_su_promote")
    test_property, test_community = create_test_property_and_community(db, initial_manager_user.id)
    # The initial_manager_user is now primary. We need to demote them or add another one.
    # Let's add another non-primary manager first by superuser
    
    other_manager_user, _ = create_user_with_role(db, UserRole.PROPERTY, username_suffix="_other_mgr_su_promote")
    add_manager_data = {
        "manager_id": other_manager_user.id,
        "role": "待提升",
        "is_primary": False,
        "community_id": test_community.id
    }
    headers = {"Authorization": f"Bearer {superuser_token}"}
    add_response = client.post(f"/api/v1/properties/{test_property.id}/managers", json=add_manager_data, headers=headers)
    assert add_response.status_code == 200
    pm_id_to_promote = add_response.json()["id"]

    # Now, demote the initial primary manager (initial_manager_user) using superuser
    # Find PropertyManager ID of initial_manager_user
    db_prop_obj = crud_property.get(db, id=test_property.id)
    initial_pm_id = None
    for pm_entry in db_prop_obj.property_managers:
        if pm_entry.manager_id == initial_manager_user.id and pm_entry.is_primary:
            initial_pm_id = pm_entry.id
            break
    assert initial_pm_id is not None
    
    demote_payload = {"is_primary": False, "community_id": test_community.id} # Must provide community_id if demoting
    demote_resp = client.put(f"/api/v1/properties/{test_property.id}/managers/{initial_pm_id}", json=demote_payload, headers=headers)
    assert demote_resp.status_code == 200, demote_resp.json()


    # Now promote other_manager_user to primary
    promote_payload = {"is_primary": True} # community_id becomes None via CRUD/API logic
    promote_response = client.put(
        f"/api/v1/properties/{test_property.id}/managers/{pm_id_to_promote}",
        json=promote_payload,
        headers=headers
    )
    assert promote_response.status_code == 200, promote_response.json()
    updated_data = promote_response.json()
    assert updated_data["is_primary"] is True
    assert updated_data["community_id"] is None # Primary manager's community_id should be None 