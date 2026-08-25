from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.permission.model import Permission
from api.role.model import RolePermission
from infra.db.base_repository import BaseRepository


class PermissionRepository(BaseRepository[Permission]):
    """提供权限数据访问操作。"""

    def __init__(self, db: AsyncSession):
        super().__init__(Permission, db)

    async def get_by_code(self, code: str) -> Permission | None:
        """按权限编码查询权限。"""
        return await self.get(Permission.code == code)

    async def get_by_ids(self, ids: list[str]) -> list[Permission]:
        """按权限标识批量查询权限。"""
        return await self.get_list(Permission.id.in_(ids))

    async def has_children(self, permission_id: str) -> bool:
        """判断权限下是否存在子权限。"""
        return await self.exists(Permission.parent_id == permission_id)

    async def is_granted_to_role(self, permission_id: str) -> bool:
        """判断权限是否已分配给任意角色。"""
        result = await self.db.execute(
            select(RolePermission.id).where(RolePermission.permission_id == permission_id).limit(1)
        )
        return result.first() is not None
