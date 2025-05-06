from typing import Final, Optional, List
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import PydanticObjectId
from loguru import logger
from product.config import env
from product.model.entity.product import Product
from product.error.exceptions import NotFoundError
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

MONGO_DB_URI: Final[str] = env.MONGO_DB_URI

class ProductRepository:
    """Repository für MongoDB-Zugriffe auf Produktdaten."""

    def __init__(self) -> None:
        # Platz für zukünftige Abhängigkeiten (z. B. Konfig, Logger)
        pass

    async def save(self, product: Product) -> Product:
        return await product.insert()

    async def update(self, product: Product) -> Product:
        return await product.save()

    async def find_by_id(self, product_id: PydanticObjectId) -> Optional[Product]:
        return await Product.get(product_id)

    async def find_by_id_or_throw(self, product_id: PydanticObjectId) -> Product:
        with tracer.start_as_current_span("MongoDB: find_by_id_or_throw products"):
            product = await self.find_by_id(product_id)
            if not product:
                raise NotFoundError(f"Produkt mit ID {product_id} nicht gefunden.")
            return product

    async def delete(self, product_id: PydanticObjectId) -> bool:
        result = await Product.find_one(Product.id == product_id).delete()
        return result is not None

    async def find_all(self) -> List[Product]:
        return await Product.find_all().to_list()

    async def find_paginated(self, skip: int = 0, limit: int = 10) -> List[Product]:
        return await Product.find_all().skip(skip).limit(limit).to_list()

    async def find_filtered(
    self,
    filter_dict: dict,
    skip: int = 0,
    limit: int = 10
) -> List[Product]:
        query = Product.find(filter_dict)
        return await query.skip(skip).limit(limit).to_list()
