
"""Konfiguration für Logging."""

from pathlib import Path
from typing import Final

from loguru import logger

__all__ = ["config_logger"]

LOG_FILE: Final = Path("logs") / "app.log"


def config_logger() -> None:
    """Konfiguration für Logging."""
    logger.add(LOG_FILE, rotation="1 MB")
