from datetime import datetime
from uuid import UUID

from fastapi.concurrency import run_in_threadpool

from api.auth.schema import LoginRequest, LoginResponse
from api.user.repository import UserRepository
from common.exceptions import BusinessException, ResultCodeEnum
from infra.db.base_table import SHANGHAI_TZ
from utils.jwt_utils import create_admin_token
from utils.password_utils import verify_password


class AuthService:
    """处理用户身份认证业务。"""

    def __init__(self, repository: UserRepository):
        """使用用户仓储初始化认证服务。"""
        self.repository = repository

    async def login(self, data: LoginRequest) -> LoginResponse:
        """校验登录凭据，记录登录时间并签发访问令牌。"""
        user = await self.repository.get_by_login(data.username)
        if user is None or not await run_in_threadpool(
            verify_password, data.password, user.hashed_password
        ):
            raise BusinessException(ResultCodeEnum.UNAUTHORIZED, "用户名或密码错误")
        if not user.is_active:
            raise BusinessException(ResultCodeEnum.NO_AUTH_ERROR, "用户已被禁用")

        user.last_login = datetime.now(SHANGHAI_TZ).replace(tzinfo=None)
        await self.repository.update(user)
        return LoginResponse(
            token=create_admin_token(UUID(user.id)),
        )
