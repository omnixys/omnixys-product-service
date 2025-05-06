from typing import Final, List

from beanie import PydanticObjectId
from loguru import logger

from product.error.exceptions import NotFoundError
from product.messaging.producer import KafkaProducerService
from product.model.entity.product import Product, ProductInput, ProductVariant
from product.model.entity.product_variant import ProductVariantInput
from product.repository.product_repository import ProductRepository


class ProductWriteService:
    """Service für schreibende Operationen auf Produktdaten inkl. Kafka-Publishing."""

    def __init__(
        self,
        repository: ProductRepository,
        kafka_producer: KafkaProducerService,
    ) -> None:
        self._repo: Final = repository
        self._kafka: Final = kafka_producer
        self._logger: Final = logger.bind(classname=self.__class__.__name__)

    async def create(self, input: ProductInput) -> PydanticObjectId:
        self._logger.debug("create: input=%s", input)

        product = Product(**input.dict())
        saved = await self._repo.save(product)
        await self._kafka.send_event("product-created", saved.dict())

        return saved.id

    async def update(
        self,
        product_id: PydanticObjectId,
        input: ProductInput,
    ) -> PydanticObjectId:
        logger.debug("update: id=%s input=%s", product_id, input)

        product = await self._repo.find_by_id_or_throw(product_id)
        product.update(input.dict(exclude_unset=True))
        updated = await self._repo.update(product)

        await self._kafka.send_event("product-updated", updated.dict())
        return updated.id

    async def delete(self, product_id: PydanticObjectId) -> bool:
        logger.debug("delete: id=%s", product_id)

        await self._repo.find_by_id_or_throw(product_id)
        deleted = await self._repo.delete(product_id)

        if deleted:
            await self._kafka.send_event("product-deleted", {"id": str(product_id)})

        return deleted

    async def add_variants(
        self,
        product_id: PydanticObjectId,
        variant_inputs: List[ProductVariantInput],
    ) -> PydanticObjectId:
        logger.debug("add_variants: id=%s, variants=%s", product_id, variant_inputs)

        product = await self._repo.find_by_id_or_throw(product_id)
        variants = [ProductVariant(**variant.dict()) for variant in variant_inputs]

        if product.productVariants:
            product.productVariants.extend(variants)
        else:
            product.productVariants = variants

        updated = await self._repo.update(product)
        await self._kafka.send_event("product-variant-added", updated.dict())

        return updated.id

    async def add_image_paths(
        self,
        product_id: PydanticObjectId,
        paths: List[str],
    ) -> PydanticObjectId:
        logger.debug("add_image_paths: id=%s, paths=%s", product_id, paths)

        product = await self._repo.find_by_id_or_throw(product_id)
        product.image_paths = (product.image_paths or []) + paths

        updated = await self._repo.update(product)
        await self._kafka.send_event("product-image-added", updated.dict())

        return updated.id
