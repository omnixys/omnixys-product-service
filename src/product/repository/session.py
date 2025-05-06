"""Initialisierung der Beanie-Datenbankverbindung mit MongoDB."""

from typing import Final
from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger
from beanie import init_beanie

from product.config import env
from product.model.entity.product import Product

MONGO_DB_URI: Final[str] = env.MONGO_DB_URI
MONGO_DB_NAME: Final[str] = env.MONGO_DB_DATABASE


__all__ = ["init_beanie_connection"]

client: AsyncIOMotorClient | None = None


async def init_beanie_connection() -> None:
    """Initialisiert die Verbindung zu MongoDB und Beanie."""
    global client
    logger.debug("Verbinde mit MongoDB unter {}", MONGO_DB_URI)
    client = AsyncIOMotorClient(MONGO_DB_URI)

    await init_beanie(
        database=client[MONGO_DB_NAME],
        document_models=[
            Product,
        ],
    )

    logger.info("MongoDB- und Beanie-Initialisierung abgeschlossen.")


async def dispose_connection_pool() -> None:
    """Schließt die Verbindung zum MongoDB-Client."""
    global client
    if client is not None:
        logger.info("MongoDB-Verbindung wird geschlossen.")
        client.close()
        client = None
