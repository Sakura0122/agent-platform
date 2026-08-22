from datetime import datetime
from typing import Any, cast

from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from infra.db.base_table import BaseTable, SoftDeleteMixin


class BaseRepository[T: BaseTable]:
    def __init__(self, model: type[T], db: AsyncSession):
        self.model = model
        self.db = db

    @property
    def _supports_soft_delete(self) -> bool:
        return issubclass(self.model, SoftDeleteMixin)

    async def get_by_id(self, id: str) -> T | None:
        return await self.db.get(self.model, id)

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> list[T]:
        sql = select(self.model).offset(offset).limit(limit)
        result = await self.db.execute(sql)
        return list(result.scalars().all())

    async def create(self, obj: T) -> T:
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: T) -> T:
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def delete(self, ids: list[str]) -> None:
        if not ids:
            return

        if self._supports_soft_delete:
            sql = (
                update(self.model)
                .where(
                    self.model.id.in_(ids),
                    self.model.deleted_at.is_(None),
                )
                .values(deleted_at=func.now())
            )
        else:
            sql = delete(self.model).where(self.model.id.in_(ids))

        await self.db.execute(sql)
        await self.db.flush()

    # 通用分页 + 模糊搜索
    # userRepo.get_page(0,10,"admin",["username","email"])
    # permRepo.get_page(0,10,"list",["code","name"])
    async def get_page(
        self,
        offset: int = 0,
        limit: int = 20,
        keyword: str | None = None,
        search_fields: list[str] | None = None,
    ) -> tuple[list[T], int]:
        """
        通用分页 + 模糊搜索

        参数：
            offset: 偏移量
            limit: 每页条数
            keyword: 搜索关键词
            search_fields: 要搜索的字段名列表，如 ["username", "email"]

        返回：
            (数据列表, 总条数) 的元组
        """
        sql = select(self.model)

        # 如果有关键词且指定了搜索字段，构建 OR 模糊查询
        if keyword and search_fields:
            conditions = []
            for field_name in search_fields:
                # 从某个对象中获取对应的字段对象
                column = getattr(self.model, field_name, None)
                if column is not None:
                    conditions.append(column.like(f"%{keyword}%"))
            if conditions:
                sql = sql.where(or_(*conditions))

        # 查询总数（复用相同的 WHERE 条件）
        count_stmt = select(func.count()).select_from(sql.subquery())
        total_result = await self.db.execute(count_stmt)
        # 总计数
        total = total_result.scalar_one()

        # 查询分页数据
        sql = sql.offset(offset).limit(limit).order_by(self.model.id.asc())
        result = await self.db.execute(sql)
        items = list(result.scalars().all())

        # 多个结果封装成了 元组  （数据列表, 总条数）
        return items, total
