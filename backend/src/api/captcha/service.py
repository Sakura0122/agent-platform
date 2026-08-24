import base64
import secrets
from uuid import uuid4

from captcha.image import ImageCaptcha
from redis.asyncio import Redis

from api.captcha.schema import CaptchaResponse
from core.config import settings

_CAPTCHA_KEY_PREFIX = "captcha:"
_CAPTCHA_CHARACTERS = "ABCDEFGHJKLMNPQRSTUVWXYZ2346789"


class CaptchaService:
    """处理图形验证码的生成与校验。"""

    def __init__(self, client: Redis):
        """使用 Redis 客户端初始化验证码服务。"""
        self.client = client

    async def create(self) -> CaptchaResponse:
        """生成四位大写字母数字验证码，并将答案限时保存到 Redis。"""
        captcha_id = str(uuid4())
        code = "".join(secrets.choice(_CAPTCHA_CHARACTERS) for _ in range(4))
        await self.client.set(
            f"{_CAPTCHA_KEY_PREFIX}{captcha_id}",
            code,
            ex=settings.captcha_expire_seconds,
        )
        return CaptchaResponse(
            captcha_id=captcha_id,
            image=self._render_image_data_uri(code),
        )

    async def verify(self, captcha_id: str, code: str) -> bool:
        """原子消费验证码并返回校验结果，验证码只能校验一次。"""
        stored_code = await self.client.getdel(f"{_CAPTCHA_KEY_PREFIX}{captcha_id}")
        return isinstance(stored_code, str) and secrets.compare_digest(
            stored_code,
            code,
        )

    @staticmethod
    def _render_image_data_uri(code: str) -> str:
        """将验证码答案渲染为 PNG Data URL。"""
        image = ImageCaptcha(width=160, height=56).generate(code).read()
        encoded = base64.b64encode(image).decode()
        return f"data:image/png;base64,{encoded}"
