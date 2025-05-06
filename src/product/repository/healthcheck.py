# src/product/repository/healthcheck.py

from typing import Final
from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger
from product.config import env

MONGO_DB_URI: Final[str] = env.MONGO_DB_URI


async def check_db_connection() -> bool:
    """Überprüft, ob eine Verbindung zur MongoDB-Datenbank hergestellt werden kann."""
    try:
        logger.debug("Health-Check: MongoDB URI = {}", MONGO_DB_URI)
        client = AsyncIOMotorClient(MONGO_DB_URI, serverSelectionTimeoutMS=300)
        await client.server_info()  # pingt MongoDB
        client.close()
        return True
    except Exception as ex:
        logger.error("MongoDB-Verbindung fehlgeschlagen: {}", ex)
        return False
