from sqlalchemy import CHAR, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from infra.db.base_table import BaseTable


class Permission(BaseTable):
    """接口与菜单权限。"""

    __tablename__ = "permissions"

    code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_id: Mapped[str | None] = mapped_column(CHAR(36), ForeignKey("permissions.id"))
    type: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="权限类型: 1目录, 2菜单, 3按钮"
    )
    description: Mapped[str | None] = mapped_column(String(200))
