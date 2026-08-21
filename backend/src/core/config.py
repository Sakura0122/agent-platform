from functools import lru_cache
from pathlib import Path

from pydantic import PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict

# 固定到 backend 目录，避免从不同目录启动服务时读错 .env。
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """配置类，用于读取 .env 文件中的配置。"""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "AgentPlatform"
    app_env: str = "development"

    database_url: str = ""
    database_echo: bool = False

    logger_level: str = "INFO"
    logger_dir: str = "logs"


@lru_cache
def get_settings() -> Settings:
    # 配置在服务运行期间保持不变，缓存后避免每次请求都重新读取 .env。
    return Settings()


settings = get_settings()
