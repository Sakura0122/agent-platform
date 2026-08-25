from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from api.role.schema import RoleResponse


class UserCreateRequest(BaseModel):
    """创建用户请求。"""

    username: str = Field(
        min_length=3,
        max_length=50,
        description="用户名",
    )
    email: str = Field(
        min_length=3,
        max_length=100,
        description="邮箱地址",
    )
    password: str = Field(
        min_length=8,
        max_length=128,
        description="登录密码，至少八个字符",
    )


class UserUpdateRequest(BaseModel):
    """编辑用户信息请求。"""

    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
        description="用户名",
    )
    email: str | None = Field(
        default=None,
        min_length=3,
        max_length=100,
        description="邮箱地址",
    )
    is_active: bool | None = Field(default=None, description="是否启用")
    is_superuser: bool | None = Field(default=None, description="是否为超级管理员")


class UserRoleAssignRequest(BaseModel):
    """设置用户角色请求，提交的列表将覆盖用户原有角色。"""

    role_ids: list[str] = Field(
        max_length=50,
        description="角色标识列表，传空列表表示清空用户角色",
    )


class UserResponse(BaseModel):
    """用户公开信息响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(description="用户标识")
    username: str = Field(description="用户名")
    email: str = Field(description="邮箱地址")
    is_active: bool = Field(description="是否启用")
    is_superuser: bool = Field(description="是否为超级管理员")
    last_login: datetime | None = Field(description="最后登录时间，未登录过时为空")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="最后更新时间")


class UserDetailResponse(UserResponse):
    """用户详情响应，包含用户已分配的角色。"""

    roles: list[RoleResponse] = Field(description="用户已分配的角色列表")
