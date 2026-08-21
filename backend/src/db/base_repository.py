from datetime import datetime
from typing import Any, cast

from sqlalchemy import select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from db.base_table import BaseTable


class BaseRepository[T: BaseTable]:
    def __init__(self, model: type[T], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id: str) -> T | None:
        return await self.db.get(self.model, id)

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> list[T]:
        stmt = select(self.model).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
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

    async def delete(self, obj: T) -> None:
        await self.db.delete(obj)
        await self.db.flush()

    async def soft_delete_by(self, **conditions: Any) -> int:
        """批量软删除符合条件的业务数据。"""

        result = cast(
            "CursorResult[Any]",
            await self.db.execute(
                update(self.model)
                .filter_by(**conditions)
                .where(self.model.deleted_at.is_(None))
                .values(deleted_at=datetime.now())  # noqa: DTZ005
            ),
        )
        return result.rowcount
