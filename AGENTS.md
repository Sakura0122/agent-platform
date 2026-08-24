# AGENTS.md

本文件用于约束在本仓库中工作的 AI 编码代理。除非用户明确提出例外，以下规则均为强制要求。

## 1. 基本原则

- 先阅读相关代码，再开始修改；不得凭空假设项目结构、数据模型或接口行为。
- 只实现用户明确要求的内容，不添加未要求的功能、抽象、配置或兼容逻辑。
- 修改范围应尽可能小，不顺手重构、格式化或清理无关代码。
- 保持现有技术栈和代码风格。本项目后端使用 Python、FastAPI、Pydantic、SQLAlchemy 和 `uv`。
- 新增代码应放入现有分层：`router.py` 负责 HTTP 接口，`schema.py` 负责请求与响应模型，
  `service.py` 负责业务逻辑，`repository.py` 负责数据访问，`model.py` 负责数据库模型。
- API 文档、代码注释、异常提示等面向项目维护者或用户的文字，默认使用简体中文。

## 2. 接口设计规范

### 2.1 路由职责

- 路由层只负责接收和校验参数、注入依赖、调用 Service、转换响应，不在路由中编写数据库查询或复杂业务逻辑。
- 使用 `APIRouter` 按业务模块拆分路由，并显式设置有意义的中文 `tags`。
- 路径使用小写英文和复数资源名，例如 `/users`；单词之间使用连字符，不使用下划线。
- 优先使用符合语义的 HTTP 方法：查询用 `GET`，创建用 `POST`，整体更新用 `PUT`，部分更新用
  `PATCH`，删除用 `DELETE`。
- 接口函数使用 `async def`；依赖通过 `Annotated[..., Depends(...)]` 声明。
- 请求体、路径参数、查询参数和响应均须有明确类型，不使用无约束的 `dict`、`list` 或 `Any` 代替
  已知的数据结构。
- 请求模型以 `Request` 结尾，响应模型以 `Response` 结尾；不得直接返回 SQLAlchemy 模型。
- 所有业务接口必须使用项目统一的 `Result[T]` 响应结构，并在路由装饰器中显式声明
  `response_model`。
- 所有业务接口统一返回 HTTP 200，通过 `Result.code` 表达业务处理结果；路由装饰器不得为业务结果
  设置其他 HTTP 状态码，业务错误码必须使用 `ResultCodeEnum` 中定义的值。
- 业务错误抛出 `BusinessException`，不得在各接口中自行拼接错误响应或吞掉异常。

### 2.2 参数与数据模型

- 使用 Pydantic 模型定义请求和响应，校验规则放在 Schema 中，不在路由函数内重复手工校验。
- 每个对外字段必须通过 `Field` 提供中文 `description`；需要时补充 `examples`、长度、范围、格式等
  OpenAPI 信息。
- 字符串、数字、分页参数等应声明合理边界；可复用的字段约束使用 `Annotated` 定义在对应模块的
  `schema.py` 中。
- 响应模型从 ORM 对象构造时，设置 `ConfigDict(from_attributes=True)`。
- 敏感信息（密码、令牌、密钥、验证码答案等）不得出现在响应模型、日志和 Swagger 示例中。
- 字段命名使用 `snake_case`，时间字段沿用项目现有格式，并准确标注是否允许为 `None`。

## 3. Swagger / OpenAPI 注解规范

每个新增或修改的接口都必须编写必要的 Swagger 注解。至少包括：

- 路由所属模块的中文 `tags`。
- 装饰器中的中文 `summary`，简洁说明接口动作。
- 明确的 `response_model`。
- 使用统一 `Result[T]` 的业务接口不额外声明 `status_code`；非业务接口确需使用其他 HTTP 状态码时，
  使用 `status` 常量显式声明。
- 路径参数和查询参数分别使用 `Path`、`Query` 提供中文 `description` 及必要约束。
- 请求体字段和响应字段使用 Pydantic `Field` 提供中文说明和安全、真实的示例。
- 不强制编写路由装饰器的 `description`、`response_description` 和 `responses`，避免简单接口出现
  大量重复说明；只有用户明确要求或接口存在无法通过类型与字段注释表达的特殊行为时才添加。

推荐写法：

```python
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from common.result import Result

router = APIRouter(prefix="/users", tags=["用户管理"])


class UserListResponse(BaseModel):
    total: int = Field(description="符合条件的用户总数", examples=[25])
    items: list[UserResponse] = Field(description="当前页用户列表")


@router.get(
    "",
    response_model=Result[UserListResponse],
    summary="查询用户列表",
)
async def list_users(
    service: Annotated[UserService, Depends(get_user_service)],
    page: Annotated[int, Query(ge=1, description="页码，从 1 开始")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="每页数量")] = 20,
) -> Result[UserListResponse]:
    return Result.success(await service.get_page(page, page_size))
```

示例只展示注解要求。实际编码时必须复用当前模块已有的依赖注入方式和已定义类型。

## 4. 方法与代码注释规范

- 注释用于补充代码、命名和类型标注无法直接表达的信息，不以覆盖所有函数为目标。
- 路由函数已有清晰的 Swagger `summary` 时，无需再添加同义文档字符串。
- 简单的依赖提供函数、构造方法以及含义明确的 Service、Repository 方法可以不写文档字符串。
- 方法存在关键业务规则、副作用、事务边界、特殊异常、缓存行为或其他不直观逻辑时，应添加简洁的
  中文文档字符串。
- 参数或返回值无法从类型标注清楚表达时，可在文档字符串中补充 `Args`、`Returns`、`Raises`，
  不机械重复函数签名。
- 类或 Pydantic 模型的用途无法从命名清楚判断时，再添加中文类文档字符串。
- 行内注释只用于解释不直观的业务原因、算法或约束，不逐行翻译代码。
- 注释必须与实现同步；修改行为时一并更新相关文档字符串、Swagger 注解和字段说明。

需要说明业务规则时的示例：

```python
class UserService:
    async def create(self, data: UserCreateRequest) -> UserResponse:
        """创建用户；用户名或邮箱已存在时抛出业务异常。"""
        ...
```

## 5. 禁止新增测试文件

- 不得创建、生成或补写任何测试文件，包括但不限于 `tests/`、`test_*.py`、`*_test.py`、测试夹具、
  快照和测试数据文件。
- 不得修改现有测试文件，除非用户明确要求。
- 不得为了满足覆盖率而引入测试依赖、测试配置或 mock 代码。
- 可以执行不修改测试文件的现有检查命令；验证应优先使用 Ruff、类型检查、模块导入和 OpenAPI
  Schema 生成等方式。

## 6. 完成前检查

提交结果前至少确认：

1. 复杂或不直观的逻辑已有必要注释，简单方法没有重复代码含义的冗余注释。
2. 每个新增或修改的接口都有 `summary` 和 `response_model`。
3. 请求与响应字段都有中文 `description` 和必要约束，Swagger 页面不存在含义不明的字段。
4. 接口仍使用统一 `Result[T]` 和项目异常处理机制，没有泄露敏感字段。
5. 未创建或修改任何测试文件，未触碰与需求无关的代码。
6. 在 `backend` 目录执行 `uv run ruff check src` 和 `uv run ruff format --check src`；若检查失败，
   只修复由本次改动引入的问题。
