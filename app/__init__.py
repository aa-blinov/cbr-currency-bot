from loguru import logger
import sys

from app.config import settings

logger.remove()  # Удаляем стандартный обработчик

logger.add(
    sys.stderr,
    level=settings.log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
)

logger.add(
    settings.log_dir / "bot.log",
    rotation=settings.log_rotation,
    level=settings.log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    retention="10 days",
)
