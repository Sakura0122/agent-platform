from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from api.router import api_router
from core.config import settings
from core.exception_handlers import register_exception_handlers
from core.logger import setup_logger
from infra.db.session import engine
from infra.redis.client import close_redis_client
from middlewares.logging import LoggingMiddleware


# 使用上下文管理器感知项目的生命周期
@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logger()  # 配置日志组件
    logger.info(f"{settings.app_name} 启动.. | 使用环境： {settings.app_env}")
    # 应用启动时执行
    yield
    # 应用关闭时执行
    # 关闭数据库连接池
    await engine.dispose()
    await close_redis_client()
    logger.info(f"{settings.app_name} 关闭.. ")


def create_app() -> FastAPI:
    # 创建应用
    fastapi_app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        lifespan=lifespan,
    )

    # 注册中间件
    fastapi_app.add_middleware(LoggingMiddleware)

    # 注册异常处理器
    register_exception_handlers(fastapi_app)

    # 注册 API 路由
    fastapi_app.include_router(api_router)

    return fastapi_app


# 创建fastapi 应用
app = create_app()


# 健康检查路由； 能访问通，就代表应用启动
@app.get("/api/health")
async def root():
    return {"status": "ok"}
