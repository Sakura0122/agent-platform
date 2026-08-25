from typing import Annotated

from fastapi import APIRouter, Depends, Path

from api.auth.dependencies import AuthPermission
from api.dependencies import PageQuery, SessionDep
from api.permission.repository import PermissionRepository
from api.role.repository import RoleRepository
from api.role.schema import (
    RoleCreateRequest,
    RoleDetailResponse,
    RolePermissionAssignRequest,
    RoleResponse,
    RoleUpdateRequest,
)
from api.role.service import RoleService
from common.page import PageResult
from common.result import Result

router = APIRouter(prefix="/roles", tags=["角色管理"])


def get_role_service(db: SessionDep) -> RoleService:
    """为当前请求提供角色服务。"""
    return RoleService(RoleRepository(db), PermissionRepository(db))


RoleServiceDep = Annotated[RoleService, Depends(get_role_service)]
RoleIdPath = Annotated[str, Path(description="角色标识")]


@router.post(
    "",
    response_model=Result[RoleResponse],
    summary="创建角色",
    dependencies=[Depends(AuthPermission(["role:create"]))],
)
async def create_role(
    data: RoleCreateRequest,
    service: RoleServiceDep,
) -> Result[RoleResponse]:
    role = await service.create(data)
    return Result.success(RoleResponse.model_validate(role))


@router.patch(
    "/{role_id}",
    response_model=Result[RoleResponse],
    summary="编辑角色",
    dependencies=[Depends(AuthPermission(["role:update"]))],
)
async def update_role(
    role_id: RoleIdPath,
    data: RoleUpdateRequest,
    service: RoleServiceDep,
) -> Result[RoleResponse]:
    role = await service.update(role_id, data)
    return Result.success(RoleResponse.model_validate(role))


@router.delete(
    "/{role_id}",
    response_model=Result[None],
    summary="删除角色",
    dependencies=[Depends(AuthPermission(["role:delete"]))],
)
async def delete_role(
    role_id: RoleIdPath,
    service: RoleServiceDep,
) -> Result[None]:
    await service.delete(role_id)
    return Result.success()


@router.get(
    "",
    response_model=Result[PageResult[RoleResponse]],
    summary="分页查询角色列表",
    dependencies=[Depends(AuthPermission(["role:query"]))],
)
async def get_role_page(
    page: PageQuery,
    service: RoleServiceDep,
) -> Result[PageResult[RoleResponse]]:
    return Result.success(await service.get_page(page))


@router.get(
    "/{role_id}",
    response_model=Result[RoleDetailResponse],
    summary="获取角色详情",
    dependencies=[Depends(AuthPermission(["role:query"]))],
)
async def get_role(
    role_id: RoleIdPath,
    service: RoleServiceDep,
) -> Result[RoleDetailResponse]:
    role = await service.get_detail(role_id)
    return Result.success(RoleDetailResponse.model_validate(role))


@router.put(
    "/{role_id}/permissions",
    response_model=Result[RoleDetailResponse],
    summary="设置角色权限",
    dependencies=[Depends(AuthPermission(["role:assign"]))],
)
async def assign_role_permissions(
    role_id: RoleIdPath,
    data: RolePermissionAssignRequest,
    service: RoleServiceDep,
) -> Result[RoleDetailResponse]:
    role = await service.assign_permissions(role_id, data)
    return Result.success(RoleDetailResponse.model_validate(role))
