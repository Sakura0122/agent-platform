from typing import Annotated

from fastapi import APIRouter, Depends, Path

from api.auth.dependencies import AuthPermission
from api.dependencies import CurrentUserDep, PageQuery, SessionDep
from api.role.repository import RoleRepository
from api.user.repository import UserRepository
from api.user.schema import (
    UserCreateRequest,
    UserDetailResponse,
    UserResponse,
    UserRoleAssignRequest,
    UserUpdateRequest,
)
from api.user.service import UserService
from common.page import PageResult
from common.result import Result

router = APIRouter(prefix="/users", tags=["用户管理"])


def get_user_service(db: SessionDep) -> UserService:
    """为当前请求提供用户服务。"""
    return UserService(UserRepository(db), RoleRepository(db))


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
UserIdPath = Annotated[str, Path(description="用户标识")]


@router.post(
    "",
    response_model=Result[UserResponse],
    summary="创建用户",
    dependencies=[Depends(AuthPermission(["user:create"]))],
)
async def create_user(
    data: UserCreateRequest,
    service: UserServiceDep,
) -> Result[UserResponse]:
    user = await service.create(data)
    return Result.success(UserResponse.model_validate(user))


@router.patch(
    "/{user_id}",
    response_model=Result[UserResponse],
    summary="编辑用户信息",
    dependencies=[Depends(AuthPermission(["user:update"]))],
)
async def update_user(
    user_id: UserIdPath,
    data: UserUpdateRequest,
    service: UserServiceDep,
) -> Result[UserResponse]:
    user = await service.update(user_id, data)
    return Result.success(UserResponse.model_validate(user))


@router.delete(
    "/{user_id}",
    response_model=Result[None],
    summary="删除用户",
    dependencies=[Depends(AuthPermission(["user:delete"]))],
)
async def delete_user(
    user_id: UserIdPath,
    service: UserServiceDep,
) -> Result[None]:
    await service.delete(user_id)
    return Result.success()


@router.get(
    "",
    response_model=Result[PageResult[UserResponse]],
    summary="分页查询用户列表",
    dependencies=[Depends(AuthPermission(["user:query"]))],
)
async def get_user_page(
    page: PageQuery,
    service: UserServiceDep,
) -> Result[PageResult[UserResponse]]:
    return Result.success(await service.get_page(page))


@router.get(
    "/me",
    response_model=Result[UserResponse],
    summary="获取当前登录用户信息",
)
async def get_current_user_info(
    user: CurrentUserDep,
) -> Result[UserResponse]:
    return Result.success(UserResponse.model_validate(user))


@router.get(
    "/{user_id}",
    response_model=Result[UserDetailResponse],
    summary="获取用户详情",
    dependencies=[Depends(AuthPermission(["user:query"]))],
)
async def get_user(
    user_id: UserIdPath,
    service: UserServiceDep,
) -> Result[UserDetailResponse]:
    user = await service.get_detail(user_id)
    return Result.success(UserDetailResponse.model_validate(user))


@router.put(
    "/{user_id}/roles",
    response_model=Result[UserDetailResponse],
    summary="设置用户角色",
    dependencies=[Depends(AuthPermission(["user:assign"]))],
)
async def assign_user_roles(
    user_id: UserIdPath,
    data: UserRoleAssignRequest,
    service: UserServiceDep,
) -> Result[UserDetailResponse]:
    user = await service.assign_roles(user_id, data)
    return Result.success(UserDetailResponse.model_validate(user))
