from sqlalchemy import CHAR, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.permission.model import Permission
from infra.db.base_table import BaseTable, CoreTable


class UserRole(CoreTable):
    """用户与角色的多对多关联。"""

    __tablename__ = "user_roles"

    user_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("users.id"), nullable=False)
    role_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("roles.id"), nullable=False)


class RolePermission(CoreTable):
    """角色与权限的多对多关联。"""

    __tablename__ = "role_permissions"

    role_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("roles.id"), nullable=False)
    permission_id: Mapped[str] = mapped_column(
        CHAR(36), ForeignKey("permissions.id"), nullable=False
    )


class Role(BaseTable):
    """后台角色。"""

    __tablename__ = "roles"

    code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(200))
    permissions: Mapped[list[Permission]] = relationship(
        secondary="role_permissions",
        lazy="selectin",
    )
