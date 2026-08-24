from fastapi.concurrency import run_in_threadpool
from sqlalchemy.exc import IntegrityError

from api.user.model import User
from api.user.repository import UserRepository
from api.user.schema import UserCreateRequest, UserUpdateRequest
from common.exceptions import BusinessException, ResultCodeEnum
from utils.password_utils import hash_password


class UserService:
    """处理用户创建和编辑相关业务。"""

    def __init__(self, repository: UserRepository):
        """使用用户仓储初始化用户服务。"""
        self.repository = repository

    async def create(self, data: UserCreateRequest) -> User:
        """创建普通用户；用户名或邮箱重复时抛出业务异常。"""
        if await self.repository.get_by_username(data.username):
            raise BusinessException(ResultCodeEnum.CONFLICT, "用户名已存在")

        email = data.email.lower()
        if await self.repository.get_by_email(email):
            raise BusinessException(ResultCodeEnum.CONFLICT, "邮箱已存在")

        hashed_password = await run_in_threadpool(hash_password, data.password)
        user = User(
            username=data.username,
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
        )
        try:
            return await self.repository.create(user)
        except IntegrityError:
            raise BusinessException(ResultCodeEnum.CONFLICT, "用户名或邮箱已存在") from None

    async def update(self, user_id: str, data: UserUpdateRequest) -> User:
        """编辑用户信息；用户不存在或唯一字段重复时抛出业务异常。"""
        user = await self.repository.get_by_id(user_id)
        if user is None:
            raise BusinessException(ResultCodeEnum.NOT_FOUND_ERROR, "用户不存在")

        if data.username is not None and data.username != user.username:
            if await self.repository.get_by_username(data.username):
                raise BusinessException(ResultCodeEnum.CONFLICT, "用户名已存在")
            user.username = data.username

        if data.email is not None:
            email = data.email.lower()
            if email != user.email:
                if await self.repository.get_by_email(email):
                    raise BusinessException(ResultCodeEnum.CONFLICT, "邮箱已存在")
                user.email = email

        if data.is_active is not None:
            user.is_active = data.is_active
        if data.is_superuser is not None:
            user.is_superuser = data.is_superuser

        try:
            return await self.repository.update(user)
        except IntegrityError:
            raise BusinessException(ResultCodeEnum.CONFLICT, "用户名或邮箱已存在") from None
