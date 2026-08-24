from enum import Enum


class ResultCodeEnum(Enum):
    PARAM_ERROR = (400, "请求参数错误")
    UNAUTHORIZED = (401, "请先登录")
    NO_AUTH_ERROR = (403, "无权限")
    NOT_FOUND_ERROR = (404, "请求数据不存在")
    CONFLICT = (409, "资源已存在")
    SYSTEM_ERROR = (500, "服务器内部错误")

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message


class BusinessException(Exception):
    def __init__(self, code: int | ResultCodeEnum, message: str | None = None):
        if isinstance(code, ResultCodeEnum):
            self.code = code.code
            self.message = message or code.message
        else:
            self.code = code
            self.message = message or "请求处理失败"

        super().__init__(self.message)
