from typing import Annotated

from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from api.captcha.schema import CaptchaResponse
from api.captcha.service import CaptchaService
from common.result import Result
from infra.redis.client import get_redis_client

router = APIRouter(prefix="/captcha", tags=["验证码"])


def get_captcha_service(
    client: Annotated[Redis, Depends(get_redis_client)],
) -> CaptchaService:
    """为当前请求提供验证码服务。"""
    return CaptchaService(client)


@router.get(
    "",
    response_model=Result[CaptchaResponse],
    summary="获取图形验证码",
)
async def get_captcha(
    service: Annotated[CaptchaService, Depends(get_captcha_service)],
) -> Result[CaptchaResponse]:
    """生成并返回一个图形验证码。"""
    return Result.success(await service.create())
