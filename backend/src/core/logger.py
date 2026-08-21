import sys
from pathlib import Path

from loguru import logger

from core.config import settings


# 项目一启动，必须自己调用这个方法，配置好日志组件的工作规则
def setup_logger() -> None:
    logger.remove()

    # 控制台
    logger.add(
        sys.stdout,
        level=settings.logger_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        colorize=True,
    )

    # 文件
    log_dir = Path(settings.logger_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    logger.add(
        str(log_dir / "{time:YYYY-MM-DD}.log"),
        level=settings.logger_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="00:00",
        retention="30 days",
        compression="gz",
        encoding="utf-8",
    )
