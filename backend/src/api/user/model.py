from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.role.model import Role
from infra.db.base_table import BaseTable


class User(BaseTable):
    """后台登录用户数据库模型。"""

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_login: Mapped[datetime | None] = mapped_column(DateTime)
    roles: Mapped[list[Role]] = relationship(
        secondary="user_roles",
        lazy="selectin",
    )
