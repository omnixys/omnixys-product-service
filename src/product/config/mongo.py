"""
MongoDB-Verbindung initialisieren für Beanie + Motor.
"""

from typing import Final

from beanie import init_beanie
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient

from product.config.env import env
from product.model.entity.product import Product

__all__ = ["init_mongo"]

# Konfiguration aus der .env via pydantic-settings
MONGO_DB_URI: Final[str] = env.MONGO_DB_URI
MONGO_DB_DATABASE: Final[str] = env.MONGO_DB_DATABASE

# Der globale Client kann bei Bedarf wiederverwendet werden
client: Final = AsyncIOMotorClient(MONGO_DB_URI)


async def init_mongo() -> None:
    """
    Initialisiert die Verbindung zur MongoDB und registriert Beanie-Modelle.
    Wird beim Startup ausgeführt.
    """
    logger.info("🔌 Initialisiere MongoDB-Client mit URI {}", MONGO_DB_URI)

    await init_beanie(
        database=client[MONGO_DB_DATABASE],
        document_models=[
            Product,
            # Weitere Beanie-Modelle hier hinzufügen
        ],
    )

    logger.success(
        "✅ MongoDB-Initialisierung abgeschlossen (DB: {})", MONGO_DB_DATABASE
    )
