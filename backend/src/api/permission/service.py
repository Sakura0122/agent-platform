from sqlalchemy.exc import IntegrityError

from api.permission.model import Permission
from api.permission.repository import PermissionRepository
from api.permission.schema import (
    PermissionCreateRequest,
    PermissionTreeResponse,
    PermissionUpdateRequest,
)
from common.exceptions import BusinessException, ResultCodeEnum


class PermissionService:
    """处理权限的增删改查业务。"""

    def __init__(self, repository: PermissionRepository):
        self.repository = repository

    async def create(self, data: PermissionCreateRequest) -> Permission:
        # 1. 校验权限编码唯一性
        if await self.repository.get_by_code(data.code):
            raise BusinessException(ResultCodeEnum.CONFLICT, "权限编码已存在")

        # 2. 校验父级权限存在
        await self._ensure_parent_valid(data.parent_id)

        # 3. 保存权限
        permission = Permission(
            code=data.code,
            name=data.name,
            type=data.type,
            parent_id=data.parent_id,
            description=data.description,
        )
        try:
            return await self.repository.create(permission)
        except IntegrityError:
            raise BusinessException(ResultCodeEnum.CONFLICT, "权限编码已存在") from None

    async def update(self, permission_id: str, data: PermissionUpdateRequest) -> Permission:
        # 1. 查询待编辑权限
        permission = await self.repository.get_by_id(permission_id)
        if permission is None:
            raise BusinessException(ResultCodeEnum.NOT_FOUND_ERROR, "权限不存在")

        # 2. 校验权限编码唯一性
        if data.code is not None and data.code != permission.code:
            if await self.repository.get_by_code(data.code):
                raise BusinessException(ResultCodeEnum.CONFLICT, "权限编码已存在")
            permission.code = data.code

        # 3. 校验并调整父级权限
        if "parent_id" in data.model_fields_set:
            await self._ensure_parent_valid(data.parent_id, permission_id)
            permission.parent_id = data.parent_id

        # 4. 更新其余字段并保存
        if data.name is not None:
            permission.name = data.name
        if data.type is not None:
            permission.type = data.type
        if "description" in data.model_fields_set:
            permission.description = data.description

        try:
            return await self.repository.update(permission)
        except IntegrityError:
            raise BusinessException(ResultCodeEnum.CONFLICT, "权限编码已存在") from None

    async def delete(self, permission_id: str) -> None:
        # 1. 查询待删除权限
        if await self.repository.get_by_id(permission_id) is None:
            raise BusinessException(ResultCodeEnum.NOT_FOUND_ERROR, "权限不存在")

        # 2. 存在子权限或已被角色引用时禁止删除
        if await self.repository.has_children(permission_id):
            raise BusinessException(ResultCodeEnum.CONFLICT, "存在子权限，不能删除")
        if await self.repository.is_granted_to_role(permission_id):
            raise BusinessException(ResultCodeEnum.CONFLICT, "权限已分配给角色，不能删除")

        # 3. 删除权限
        await self.repository.delete([permission_id])

    async def get_detail(self, permission_id: str) -> Permission:
        permission = await self.repository.get_by_id(permission_id)
        if permission is None:
            raise BusinessException(ResultCodeEnum.NOT_FOUND_ERROR, "权限不存在")
        return permission

    async def get_tree(self) -> list[PermissionTreeResponse]:
        """按父子关系组装完整权限树，同级按权限类型和编码排序。"""
        permissions = sorted(
            await self.repository.get_all(), key=lambda item: (item.type, item.code)
        )
        nodes = {item.id: PermissionTreeResponse.model_validate(item) for item in permissions}

        roots: list[PermissionTreeResponse] = []
        for item in permissions:
            parent = nodes.get(item.parent_id)
            (parent.children if parent else roots).append(nodes[item.id])
        return roots

    async def _ensure_parent_valid(
        self, parent_id: str | None, permission_id: str | None = None
    ) -> None:
        """沿父级链向上校验，确保父级权限存在且权限不会挂到自身的下级上。"""
        current = parent_id
        while current is not None:
            if current == permission_id:
                raise BusinessException(ResultCodeEnum.PARAM_ERROR, "父级权限不能为自身或其下级")

            parent = await self.repository.get_by_id(current)
            if parent is None:
                raise BusinessException(ResultCodeEnum.NOT_FOUND_ERROR, "父级权限不存在")
            current = parent.parent_id
