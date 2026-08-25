from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.role.model import Role, UserRole
from infra.db.base_repository import BaseRepository


class RoleRepository(BaseRepository[Role]):
    """提供角色数据访问操作。"""

    def __init__(self, db: AsyncSession):
        super().__init__(Role, db)

    async def get_by_code(self, code: str) -> Role | None:
        """按角色编码查询角色。"""
        return await self.get(Role.code == code)

    async def get_by_ids(self, ids: list[str]) -> list[Role]:
        """按角色标识批量查询角色。"""
        return await self.get_list(Role.id.in_(ids))

    async def is_assigned_to_user(self, role_id: str) -> bool:
        """判断角色是否已分配给任意用户。"""
        result = await self.db.execute(
            select(UserRole.id).where(UserRole.role_id == role_id).limit(1)
        )
        return result.first() is not None
