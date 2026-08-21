from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.exceptions import HTTPException

from common.exceptions import BusinessException, ResultCodeEnum
from common.result import Result


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        result = Result.error(
            ResultCodeEnum.PARAM_ERROR.code,
            ResultCodeEnum.PARAM_ERROR.message,
        )
        return JSONResponse(status_code=200, content=result.model_dump())

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        result = Result.error(exc.status_code, str(exc.detail))
        return JSONResponse(status_code=200, content=result.model_dump())

    @app.exception_handler(BusinessException)
    async def business_exception_handler(request: Request, exc: BusinessException):
        result = Result.error(exc.code, exc.message)
        return JSONResponse(status_code=200, content=result.model_dump())

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception: {exc}")
        result = Result.error(
            ResultCodeEnum.SYSTEM_ERROR.code,
            ResultCodeEnum.SYSTEM_ERROR.message,
        )
        return JSONResponse(status_code=200, content=result.model_dump())
