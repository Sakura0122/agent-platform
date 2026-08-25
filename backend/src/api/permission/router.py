from typing import Annotated

from fastapi import APIRouter, Depends, Path

from api.auth.dependencies import AuthPermission
from api.dependencies import SessionDep
from api.permission.repository import PermissionRepository
from api.permission.schema import (
    PermissionCreateRequest,
    PermissionResponse,
    PermissionTreeResponse,
    PermissionUpdateRequest,
)
from api.permission.service import PermissionService
from common.result import Result

router = APIRouter(prefix="/permissions", tags=["权限管理"])


def get_permission_service(db: SessionDep) -> PermissionService:
    """为当前请求提供权限服务。"""
    return PermissionService(PermissionRepository(db))


PermissionServiceDep = Annotated[PermissionService, Depends(get_permission_service)]
PermissionIdPath = Annotated[str, Path(description="权限标识")]


@router.post(
    "",
    response_model=Result[PermissionResponse],
    summary="创建权限",
    dependencies=[Depends(AuthPermission(["permission:create"]))],
)
async def create_permission(
    data: PermissionCreateRequest,
    service: PermissionServiceDep,
) -> Result[PermissionResponse]:
    permission = await service.create(data)
    return Result.success(PermissionResponse.model_validate(permission))


@router.patch(
    "/{permission_id}",
    response_model=Result[PermissionResponse],
    summary="编辑权限",
    dependencies=[Depends(AuthPermission(["permission:update"]))],
)
async def update_permission(
    permission_id: PermissionIdPath,
    data: PermissionUpdateRequest,
    service: PermissionServiceDep,
) -> Result[PermissionResponse]:
    permission = await service.update(permission_id, data)
    return Result.success(PermissionResponse.model_validate(permission))


@router.delete(
    "/{permission_id}",
    response_model=Result[None],
    summary="删除权限",
    dependencies=[Depends(AuthPermission(["permission:delete"]))],
)
async def delete_permission(
    permission_id: PermissionIdPath,
    service: PermissionServiceDep,
) -> Result[None]:
    await service.delete(permission_id)
    return Result.success()


@router.get(
    "",
    response_model=Result[list[PermissionTreeResponse]],
    summary="获取权限树",
    dependencies=[Depends(AuthPermission(["permission:query"]))],
)
async def get_permission_tree(
    service: PermissionServiceDep,
) -> Result[list[PermissionTreeResponse]]:
    return Result.success(await service.get_tree())


@router.get(
    "/{permission_id}",
    response_model=Result[PermissionResponse],
    summary="获取权限详情",
    dependencies=[Depends(AuthPermission(["permission:query"]))],
)
async def get_permission(
    permission_id: PermissionIdPath,
    service: PermissionServiceDep,
) -> Result[PermissionResponse]:
    permission = await service.get_detail(permission_id)
    return Result.success(PermissionResponse.model_validate(permission))
