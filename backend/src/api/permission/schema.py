from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PermissionCreateRequest(BaseModel):
    """创建权限请求。"""

    code: str = Field(
        min_length=2,
        max_length=100,
        description="权限编码，接口鉴权时使用",
        examples=["user:create"],
    )
    name: str = Field(
        min_length=1,
        max_length=100,
        description="权限名称",
        examples=["创建用户"],
    )
    type: int = Field(
        ge=1,
        le=3,
        description="权限类型: 1目录, 2菜单, 3按钮",
        examples=[3],
    )
    parent_id: str | None = Field(
        default=None,
        max_length=36,
        description="父级权限标识，顶级权限为空",
    )
    description: str | None = Field(
        default=None,
        max_length=200,
        description="权限描述",
        examples=["允许在用户管理页面新增用户"],
    )


class PermissionUpdateRequest(BaseModel):
    """编辑权限请求，仅提交需要修改的字段。"""

    code: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
        description="权限编码，接口鉴权时使用",
    )
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="权限名称",
    )
    type: int | None = Field(
        default=None,
        ge=1,
        le=3,
        description="权限类型: 1目录, 2菜单, 3按钮",
    )
    parent_id: str | None = Field(
        default=None,
        max_length=36,
        description="父级权限标识，显式传 null 表示调整为顶级权限",
    )
    description: str | None = Field(
        default=None,
        max_length=200,
        description="权限描述，显式传 null 表示清空",
    )


class PermissionResponse(BaseModel):
    """权限信息响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(description="权限标识")
    code: str = Field(description="权限编码")
    name: str = Field(description="权限名称")
    type: int = Field(description="权限类型: 1目录, 2菜单, 3按钮")
    parent_id: str | None = Field(description="父级权限标识，顶级权限为空")
    description: str | None = Field(description="权限描述")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="最后更新时间")


class PermissionTreeResponse(PermissionResponse):
    """权限树节点响应，children 为空数组表示叶子节点。"""

    children: list[PermissionTreeResponse] = Field(
        default_factory=list,
        description="子权限列表",
    )
