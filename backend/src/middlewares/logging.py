import time

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


# 日志中间件； 用于记录请求的处理时间。
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()

        # 放行请求。
        response = await call_next(request)

        elapsed = (time.perf_counter() - start) * 1000
        logger.info(
            f"<-- {request.method} {request.url.path} status={response.status_code} {elapsed:.2f}ms"
        )
        return response
