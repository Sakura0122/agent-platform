from sqlalchemy.exc import IntegrityError

from api.permission.repository import PermissionRepository
from api.role.model import Role
from api.role.repository import RoleRepository
from api.role.schema import (
    RoleCreateRequest,
    RolePermissionAssignRequest,
    RoleResponse,
    RoleUpdateRequest,
)
from common.exceptions import BusinessException, ResultCodeEnum
from common.page import PageRequest, PageResult

_SORT_FIELDS = {
    "code": Role.code,
    "name": Role.name,
    "created_at": Role.created_at,
}


class RoleService:
    """处理角色的增删改查以及角色权限分配业务。"""

    def __init__(self, repository: RoleRepository, permission_repository: PermissionRepository):
        self.repository = repository
        self.permission_repository = permission_repository

    async def create(self, data: RoleCreateRequest) -> Role:
        # 1. 校验角色编码唯一性
        if await self.repository.get_by_code(data.code):
            raise BusinessException(ResultCodeEnum.CONFLICT, "角色编码已存在")

        # 2. 保存角色
        role = Role(code=data.code, name=data.name, description=data.description)
        try:
            return await self.repository.create(role)
        except IntegrityError:
            raise BusinessException(ResultCodeEnum.CONFLICT, "角色编码已存在") from None

    async def update(self, role_id: str, data: RoleUpdateRequest) -> Role:
        # 1. 查询待编辑角色
        role = await self.repository.get_by_id(role_id)
        if role is None:
            raise BusinessException(ResultCodeEnum.NOT_FOUND_ERROR, "角色不存在")

        # 2. 校验角色编码唯一性
        if data.code is not None and data.code != role.code:
            if await self.repository.get_by_code(data.code):
                raise BusinessException(ResultCodeEnum.CONFLICT, "角色编码已存在")
            role.code = data.code

        # 3. 更新其余字段并保存
        if data.name is not None:
            role.name = data.name
        if "description" in data.model_fields_set:
            role.description = data.description

        try:
            return await self.repository.update(role)
        except IntegrityError:
            raise BusinessException(ResultCodeEnum.CONFLICT, "角色编码已存在") from None

    async def delete(self, role_id: str) -> None:
        # 1. 查询待删除角色
        if await self.repository.get_by_id(role_id) is None:
            raise BusinessException(ResultCodeEnum.NOT_FOUND_ERROR, "角色不存在")

        # 2. 已分配给用户的角色禁止删除
        if await self.repository.is_assigned_to_user(role_id):
            raise BusinessException(ResultCodeEnum.CONFLICT, "角色已分配给用户，不能删除")

        # 3. 删除角色
        await self.repository.delete([role_id])

    async def get_detail(self, role_id: str) -> Role:
        role = await self.repository.get_by_id(role_id)
        if role is None:
            raise BusinessException(ResultCodeEnum.NOT_FOUND_ERROR, "角色不存在")
        return role

    async def get_page(self, page: PageRequest) -> PageResult[RoleResponse]:
        roles, total = await self.repository.get_page(
            offset=page.offset,
            limit=page.page_size,
            keyword=page.keyword,
            search_fields=["code", "name"],
            order_by=page.to_order_by(_SORT_FIELDS),
        )
        return PageResult.of(page, total, [RoleResponse.model_validate(role) for role in roles])

    async def assign_permissions(self, role_id: str, data: RolePermissionAssignRequest) -> Role:
        """使用提交的权限列表覆盖角色原有权限。"""
        # 1. 查询目标角色
        role = await self.repository.get_by_id(role_id)
        if role is None:
            raise BusinessException(ResultCodeEnum.NOT_FOUND_ERROR, "角色不存在")

        # 2. 校验权限标识全部有效
        permissions = await self.permission_repository.get_by_ids(data.permission_ids)
        if len(permissions) != len(set(data.permission_ids)):
            raise BusinessException(ResultCodeEnum.NOT_FOUND_ERROR, "存在无效的权限标识")

        # 3. 覆盖角色权限并保存
        role.permissions = permissions
        return await self.repository.update(role)
