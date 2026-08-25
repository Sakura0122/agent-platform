from fastapi.concurrency import run_in_threadpool
from sqlalchemy.exc import IntegrityError

from api.role.repository import RoleRepository
from api.user.model import User
from api.user.repository import UserRepository
from api.user.schema import (
    UserCreateRequest,
    UserResponse,
    UserRoleAssignRequest,
    UserUpdateRequest,
)
from common.exceptions import BusinessException, ResultCodeEnum
from common.page import PageRequest, PageResult
from utils.password_utils import hash_password

_SORT_FIELDS = {
    "username": User.username,
    "email": User.email,
    "last_login": User.last_login,
    "created_at": User.created_at,
}


class UserService:
    """处理用户增删改查以及用户角色分配相关业务。"""

    def __init__(self, repository: UserRepository, role_repository: RoleRepository):
        """使用用户仓储和角色仓储初始化用户服务。"""
        self.repository = repository
        self.role_repository = role_repository

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

    async def delete(self, user_id: str) -> None:
        """删除用户；用户不存在时抛出业务异常。"""
        if await self.repository.get_by_id(user_id) is None:
            raise BusinessException(ResultCodeEnum.NOT_FOUND_ERROR, "用户不存在")

        await self.repository.delete([user_id])

    async def get_detail(self, user_id: str) -> User:
        user = await self.repository.get_by_id(user_id)
        if user is None:
            raise BusinessException(ResultCodeEnum.NOT_FOUND_ERROR, "用户不存在")
        return user

    async def get_page(self, page: PageRequest) -> PageResult[UserResponse]:
        users, total = await self.repository.get_page(
            offset=page.offset,
            limit=page.page_size,
            keyword=page.keyword,
            search_fields=["username", "email"],
            order_by=page.to_order_by(_SORT_FIELDS),
        )
        return PageResult.of(page, total, [UserResponse.model_validate(user) for user in users])

    async def assign_roles(self, user_id: str, data: UserRoleAssignRequest) -> User:
        """使用提交的角色列表覆盖用户原有角色。"""
        # 1. 查询目标用户
        user = await self.repository.get_by_id(user_id)
        if user is None:
            raise BusinessException(ResultCodeEnum.NOT_FOUND_ERROR, "用户不存在")

        # 2. 校验角色标识全部有效
        roles = await self.role_repository.get_by_ids(data.role_ids)
        if len(roles) != len(set(data.role_ids)):
            raise BusinessException(ResultCodeEnum.NOT_FOUND_ERROR, "存在无效的角色标识")

        # 3. 覆盖用户角色并保存
        user.roles = roles
        return await self.repository.update(user)
