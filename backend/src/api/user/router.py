from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user
from api.user.model import User
from api.user.repository import UserRepository
from api.user.schema import UserCreateRequest, UserResponse, UserUpdateRequest
from api.user.service import UserService
from common.result import Result
from infra.db.session import get_session

router = APIRouter(prefix="/users", tags=["用户管理"])


def get_user_service(
    db: Annotated[AsyncSession, Depends(get_session)],
) -> UserService:
    """为当前请求提供用户服务。"""
    return UserService(UserRepository(db))


@router.post(
    "",
    response_model=Result[UserResponse],
    summary="创建用户",
)
async def create_user(
    data: UserCreateRequest,
    service: Annotated[UserService, Depends(get_user_service)],
) -> Result[UserResponse]:
    user = await service.create(data)
    return Result.success(UserResponse.model_validate(user))


@router.patch(
    "/{user_id}",
    response_model=Result[UserResponse],
    summary="编辑用户信息",
)
async def update_user(
    user_id: Annotated[str, Path(description="用户标识")],
    data: UserUpdateRequest,
    service: Annotated[UserService, Depends(get_user_service)],
) -> Result[UserResponse]:
    user = await service.update(user_id, data)
    return Result.success(UserResponse.model_validate(user))


@router.get(
    "/me",
    response_model=Result[UserResponse],
    summary="获取当前登录用户信息",
)
async def get_current_user_info(
    user: Annotated[User, Depends(get_current_user)],
) -> Result[UserResponse]:
    return Result.success(UserResponse.model_validate(user))
