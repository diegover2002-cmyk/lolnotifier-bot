import sys
from pathlib import Path
from loguru import logger

def setup_logger():
    log_dir = Path('/app/logs')
    log_dir.mkdir(exist_ok=True)

    # Remove default sink
    logger.remove()

    # Console (live docker logs)
    logger.add(sys.stdout,
               format='<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}:{function}:{line}</cyan> | <level>{message}</level>',
               level="INFO",
               colorize=True)

    # File rotate (persist)
    logger.add(log_dir / "bot.log",
               rotation="10 MB",
               retention="7 days",
               level="DEBUG",
               format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
               serialize=False)

    logger.info("Logger configurado: console + bot.log rotate")
    return logger

