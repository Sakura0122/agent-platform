from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from api.permission.schema import PermissionResponse


class RoleCreateRequest(BaseModel):
    """创建角色请求。"""

    code: str = Field(
        min_length=2,
        max_length=100,
        description="角色编码",
        examples=["system:admin"],
    )
    name: str = Field(
        min_length=1,
        max_length=100,
        description="角色名称",
        examples=["系统管理员"],
    )
    description: str | None = Field(
        default=None,
        max_length=200,
        description="角色描述",
        examples=["负责后台系统的日常维护"],
    )


class RoleUpdateRequest(BaseModel):
    """编辑角色请求，仅提交需要修改的字段。"""

    code: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
        description="角色编码",
    )
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="角色名称",
    )
    description: str | None = Field(
        default=None,
        max_length=200,
        description="角色描述，显式传 null 表示清空",
    )


class RolePermissionAssignRequest(BaseModel):
    """设置角色权限请求，提交的列表将覆盖角色原有权限。"""

    permission_ids: list[str] = Field(
        max_length=200,
        description="权限标识列表，传空列表表示清空角色权限",
    )


class RoleResponse(BaseModel):
    """角色基本信息响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(description="角色标识")
    code: str = Field(description="角色编码")
    name: str = Field(description="角色名称")
    description: str | None = Field(description="角色描述")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="最后更新时间")


class RoleDetailResponse(RoleResponse):
    """角色详情响应，包含角色已分配的权限。"""

    permissions: list[PermissionResponse] = Field(description="角色已分配的权限列表")
