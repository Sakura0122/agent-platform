from collections.abc import Sequence
from typing import Any, cast

from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from infra.db.base_table import BaseTable, CoreTable


class BaseRepository[T: CoreTable]:
    """提供基础数据库操作，事务提交和业务异常由上层负责。"""

    def __init__(self, model: type[T], db: AsyncSession):
        self.model = model
        self.db = db

    @property
    def _supports_soft_delete(self) -> bool:
        """BaseTable 支持软删除，直接继承 CoreTable 的模型使用物理删除。"""
        return issubclass(self.model, BaseTable)

    async def get(
        self,
        *conditions: ColumnElement[bool],
        include_deleted: bool = False,
    ) -> T | None:
        """按条件查询一条记录。"""
        sql = select(self.model).where(*conditions)
        if include_deleted:
            sql = sql.execution_options(include_deleted=True)

        result = await self.db.execute(sql)
        return result.scalars().first()

    async def get_by_id(self, id: str, *, include_deleted: bool = False) -> T | None:
        """按主键查询，显式查询可避免 Session 缓存绕过软删除过滤。"""
        return await self.get(self.model.id == id, include_deleted=include_deleted)

    async def get_all(
        self,
        *,
        include_deleted: bool = False,
    ) -> list[T]:
        """查询记录列表，默认按主键排序以保证分页结果稳定。"""
        sql = select(self.model).order_by(self.model.id.asc())
        if include_deleted:
            sql = sql.execution_options(include_deleted=True)

        result = await self.db.execute(sql)
        return list(result.scalars().all())

    async def count(
        self,
        *conditions: ColumnElement[bool],
        include_deleted: bool = False,
    ) -> int:
        """统计符合条件的记录数。"""
        sql = select(func.count(self.model.id)).where(*conditions)
        if include_deleted:
            sql = sql.execution_options(include_deleted=True)

        result = await self.db.execute(sql)
        return result.scalar_one()

    async def exists(
        self,
        *conditions: ColumnElement[bool],
        include_deleted: bool = False,
    ) -> bool:
        """判断是否存在符合条件的记录。"""
        return await self.count(*conditions, include_deleted=include_deleted) > 0

    async def create(self, obj: T) -> T:
        """新增记录，只 flush，不在仓储层提交事务。"""
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: T) -> T:
        """持久化已在当前 Session 中修改的对象。"""
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def delete(self, ids: list[str]) -> None:
        """BaseTable 执行软删除，CoreTable 执行物理删除。"""
        if not ids:
            return

        if self._supports_soft_delete:
            soft_delete_model = cast("type[BaseTable]", self.model)
            deleted_at = soft_delete_model.deleted_at
            sql = (
                update(self.model)
                .where(self.model.id.in_(ids), deleted_at.is_(None))
                .values(deleted_at=func.now())
            )
        else:
            sql = delete(self.model).where(self.model.id.in_(ids))

        await self.db.execute(sql)
        await self.db.flush()

    async def restore(self, ids: list[str]) -> None:
        """恢复已软删除的记录。"""
        if not ids:
            return
        if not self._supports_soft_delete:
            raise TypeError(f"{self.model.__name__} 不支持软删除恢复")

        sql = update(self.model).where(self.model.id.in_(ids)).values(deleted_at=None)
        await self.db.execute(sql)
        await self.db.flush()

    async def get_page(
        self,
        offset: int = 0,
        limit: int = 20,
        keyword: str | None = None,
        search_fields: list[str] | None = None,
        *,
        order_by: Sequence[ColumnElement[Any]] | None = None,
        include_deleted: bool = False,
    ) -> tuple[list[T], int]:
        """分页查询，可按指定字段进行关键词模糊搜索。"""
        conditions: list[ColumnElement[bool]] = []
        if keyword and search_fields:
            search_conditions: list[ColumnElement[bool]] = []
            for field_name in search_fields:
                column = getattr(self.model, field_name, None)
                if column is None:
                    raise ValueError(f"{self.model.__name__} 不存在字段: {field_name}")
                search_conditions.append(column.contains(keyword, autoescape=True))
            conditions.append(or_(*search_conditions))

        # COUNT 与数据查询共用完全相同的过滤条件。
        count_sql = select(func.count(self.model.id)).where(*conditions)
        data_sql = (
            select(self.model)
            .where(*conditions)
            .order_by(*(order_by or ()), self.model.id.asc())
            .offset(offset)
            .limit(limit)
        )
        if include_deleted:
            count_sql = count_sql.execution_options(include_deleted=True)
            data_sql = data_sql.execution_options(include_deleted=True)

        total_result = await self.db.execute(count_sql)
        result = await self.db.execute(data_sql)
        return list(result.scalars().all()), total_result.scalar_one()
