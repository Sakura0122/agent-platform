from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from common.exceptions import BusinessException, ResultCodeEnum


class PageRequest(BaseModel):
    current_page: int = Field(default=1, ge=1, description="当前页数")
    page_size: int = Field(default=20, ge=1, description="每页显示条目个数")
    keyword: str | None = Field(
        default=None, max_length=50, description="搜索关键词，匹配字段由各接口定义"
    )
    sort_field: str | None = Field(default=None, description="排序字段")
    is_asc: bool = Field(default=True, description="是否升序")

    @property
    def offset(self) -> int:
        return (self.current_page - 1) * self.page_size

    def to_order_by(self, sort_field_mapping: dict[str, Any]) -> list[Any]:
        if not self.sort_field:
            return []

        sort_column = sort_field_mapping.get(self.sort_field)
        if sort_column is None:
            raise BusinessException(ResultCodeEnum.PARAM_ERROR, "排序字段不支持")

        return [sort_column.asc() if self.is_asc else sort_column.desc()]


class PageResult[T](BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    total: int = Field(description="总条数")
    page_count: int = Field(description="总页数")
    items: list[T] = Field(alias="list", description="当前页数据")

    @classmethod
    def of(cls, page: PageRequest, total: int, items: list[T]) -> PageResult[T]:
        page_count = (total + page.page_size - 1) // page.page_size
        return cls(total=total, page_count=page_count, list=items)
