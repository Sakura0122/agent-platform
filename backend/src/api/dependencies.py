from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.dependencies import get_current_admin, get_current_user, get_current_user_id
from api.user.model import User
from common.page import PageRequest
from infra.db.session import get_session

# 为每个请求提供独立的数据库会话，并统一处理事务提交或回滚
SessionDep = Annotated[AsyncSession, Depends(get_session)]

# 将分页模型中的字段解析为查询参数
PageQuery = Annotated[PageRequest, Query()]

# 注入当前用户id
CurrentUserIdDep = Annotated[str, Depends(get_current_user_id)]

# 注入当前已登录且状态有效的用户
CurrentUserDep = Annotated[User, Depends(get_current_user)]

# 注入当前管理员，非管理员访问时抛出无权限业务异常
CurrentAdminDep = Annotated[User, Depends(get_current_admin)]
