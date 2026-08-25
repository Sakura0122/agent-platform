from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from api.user.model import User
from api.user.repository import UserRepository
from common.exceptions import BusinessException, ResultCodeEnum
from infra.db.session import get_session
from utils.jwt_utils import parse_admin_token

_bearer_scheme = HTTPBearer(auto_error=False)
BearerCredentialsDep = Annotated[
    HTTPAuthorizationCredentials | None,
    Depends(_bearer_scheme),
]


async def get_current_user_id(credentials: BearerCredentialsDep) -> str:
    """解析 Bearer 令牌并返回用户标识，不查询数据库。"""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise BusinessException(ResultCodeEnum.UNAUTHORIZED)

    return str(parse_admin_token(credentials.credentials))


async def get_current_user(
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    """查询并返回当前有效用户。"""
    user = await UserRepository(db).get_by_id(user_id)
    if user is None:
        raise BusinessException(ResultCodeEnum.UNAUTHORIZED, "登录用户不存在")
    if not user.is_active:
        raise BusinessException(ResultCodeEnum.NO_AUTH_ERROR, "用户已被禁用")
    return user


async def get_current_admin(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    """返回当前管理员；普通用户访问时抛出无权限业务异常。"""
    if not user.is_superuser:
        raise BusinessException(ResultCodeEnum.NO_AUTH_ERROR, "仅管理员可执行此操作")
    return user


class AuthPermission:
    """校验登录态，并检查当前用户是否具备指定接口权限码。"""

    def __init__(self, permissions: list[str] | None = None) -> None:
        self.permissions = permissions or []

    async def __call__(self, user: Annotated[User, Depends(get_current_user)]) -> User:
        if (
            user.is_superuser
            or not self.permissions
            or "*" in self.permissions
            or "*:*:*" in self.permissions
        ):
            return user

        user_permissions = {
            permission.code for role in user.roles for permission in role.permissions
        }
        if not any(code in user_permissions for code in self.permissions):
            raise BusinessException(ResultCodeEnum.NO_AUTH_ERROR, "无权限操作")
        return user
