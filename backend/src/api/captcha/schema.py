from pydantic import BaseModel, Field


class CaptchaResponse(BaseModel):
    """图形验证码响应。"""

    captcha_id: str = Field(
        description="验证码唯一标识，用于提交验证码答案",
    )
    image: str = Field(description="PNG 格式的 Base64 Data URL")
