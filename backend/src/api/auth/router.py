from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.schema import LoginRequest, LoginResponse
from api.auth.service import AuthService
from api.user.repository import UserRepository
from common.result import Result
from infra.db.session import get_session

router = APIRouter(prefix="/auth", tags=["认证"])


def get_auth_service(
    db: Annotated[AsyncSession, Depends(get_session)],
) -> AuthService:
    """为当前请求提供认证服务。"""
    return AuthService(UserRepository(db))


@router.post(
    "/login",
    response_model=Result[LoginResponse],
    summary="用户登录",
)
async def login(
    data: LoginRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> Result[LoginResponse]:
    """使用用户名或邮箱及密码登录。"""
    return Result.success(await service.login(data))
