from typing import Annotated

from fastapi import APIRouter, Depends

from api.auth.schema import LoginRequest, LoginResponse
from api.auth.service import AuthService
from api.dependencies import SessionDep
from api.user.repository import UserRepository
from common.result import Result

router = APIRouter(prefix="/auth", tags=["认证"])


def get_auth_service(db: SessionDep) -> AuthService:
    """为当前请求提供认证服务。"""
    return AuthService(UserRepository(db))


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


@router.post(
    "/login",
    response_model=Result[LoginResponse],
    summary="用户登录",
)
async def login(
    data: LoginRequest,
    service: AuthServiceDep,
) -> Result[LoginResponse]:
    """使用用户名或邮箱及密码登录。"""
    return Result.success(await service.login(data))
