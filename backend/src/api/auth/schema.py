from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """用户登录请求。"""

    username: str = Field(
        min_length=1,
        max_length=100,
        description="用户名或邮箱",
    )
    password: str = Field(
        min_length=1,
        max_length=128,
        description="登录密码",
    )


class LoginResponse(BaseModel):
    """登录成功后返回的访问令牌。"""

    token: str = Field(description="Bearer 访问令牌")
