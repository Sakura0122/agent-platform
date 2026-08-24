from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession

from api.user.model import User
from infra.db.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """提供用户数据访问操作。"""

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_username(self, username: str) -> User | None:
        """按用户名查询用户。"""
        return await self.get(User.username == username)

    async def get_by_email(self, email: str) -> User | None:
        """按邮箱查询用户。"""
        return await self.get(User.email == email)

    async def get_by_login(self, login: str) -> User | None:
        """按用户名或邮箱查询登录用户。"""
        return await self.get(or_(User.username == login, User.email == login.lower()))
