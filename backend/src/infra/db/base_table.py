from datetime import datetime
from typing import Any
from uuid import uuid7

from sqlalchemy import CHAR, DateTime, FetchedValue, event, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    with_loader_criteria,
)


class MappedBase(DeclarativeBase):
    __abstract__ = True

class CoreTable(MappedBase):
    """只包含所有表都有的字段。"""

    __abstract__ = True

    id: Mapped[str] = mapped_column(
        CHAR(36), primary_key=True, default=lambda: str(uuid7()), comment="业务表主键 UUID"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        server_onupdate=FetchedValue(),
        comment="最后更新时间",
    )

class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime)

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now()  # noqa: DTZ005
    

class BaseTable(SoftDeleteMixin, CoreTable):
    """默认业务模型基类，支持软删除。"""

    __abstract__ = True


@event.listens_for(Session, "before_flush")
def _convert_deletes_to_soft_deletes(
    session: Session, _flush_context: Any, _instances: Any
) -> None:
    for instance in tuple(session.deleted):
        if isinstance(instance, BaseTable):
            instance.soft_delete()
            session.add(instance)


@event.listens_for(Session, "do_orm_execute")
def _exclude_deleted_rows(execute_state: Any) -> None:
    if (
        not execute_state.is_select
        or execute_state.is_column_load
        or execute_state.is_relationship_load
        or execute_state.execution_options.get("include_deleted", False)
    ):
        return

    execute_state.statement = execute_state.statement.options(
        with_loader_criteria(
            BaseTable,
            lambda model: model.deleted_at.is_(None),
            include_aliases=True,
        )
    )
