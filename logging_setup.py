"""
Logging configuration.
Uses stdlib logging (consistent with all other modules).
Call setup_logging() once at startup in main.py.
"""
from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path


def setup_logging(log_dir: str = "logs", level: int = logging.INFO) -> None:
    """
    Configure root logger with:
      - Console handler (stdout, INFO+)
      - Rotating file handler (logs/bot.log, DEBUG+, 10 MB, 7 backups)

    Args:
        log_dir: Directory for log files (created if missing).
        level:   Minimum log level for the console handler.
    """
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    fmt = logging.Formatter(
        fmt="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)  # handlers filter individually

    # Console
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(fmt)

    # Rotating file
    file_handler = logging.handlers.RotatingFileHandler(
        log_path / "bot.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=7,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)

    # Avoid duplicate handlers on re-import
    if not root.handlers:
        root.addHandler(console)
        root.addHandler(file_handler)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)

    logging.getLogger(__name__).info("Logging configured: console + %s/bot.log", log_dir)
