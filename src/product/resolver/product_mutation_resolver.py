from typing import Final, List
from uuid import UUID

from loguru import logger
from strawberry.types import Info

from product.model.entity.product import ProductInput
from product.model.entity.product_variant import ProductVariantInput
from product.model.payload.create_payload import CreatePayload
from product.security.keycloak_service import KeycloakService
from product.service.product_write_service import ProductWriteService


class ProductMutationResolver:
    """Resolver für Mutationen im Produktkontext."""

    def __init__(self, write_service: ProductWriteService):
        self.write_service = write_service

    async def create_product(self, input: ProductInput, info: Info) -> CreatePayload:
        logger.debug("create_product: input={}", input)

        keycloak: KeycloakService = info.context["keycloak"]
        keycloak.assert_roles(["Admin"])

        product_id = await self.write_service.create(input, token=keycloak.token)
        return CreatePayload(id=product_id)

    async def add_variant(
        self,
        product_id: UUID,
        input: List[ProductVariantInput],
        info: Info,
    ) -> CreatePayload:
        logger.debug("add_variant: product_id={}, variants={}", product_id, input)

        keycloak: KeycloakService = info.context["keycloak"]
        keycloak.assert_roles(["Admin"])

        updated_id = await self.write_service.add_variants(
            product_id, input, token=keycloak.token
        )
        return CreatePayload(id=updated_id)

    async def add_image_paths(
        self,
        product_id: UUID,
        paths: List[str],
        info: Info,
    ) -> CreatePayload:
        logger.debug("add_image_paths: product_id={}, paths={}", product_id, paths)

        keycloak: KeycloakService = info.context["keycloak"]
        keycloak.assert_roles(["Admin"])

        updated_id = await self.write_service.add_image_paths(
            product_id, paths, token=keycloak.token
        )
        return CreatePayload(id=updated_id)

    async def update_product(
        self,
        product_id: UUID,
        input: ProductInput,
        info: Info,
    ) -> CreatePayload:
        logger.debug("update_product: id={}, input={}", product_id, input)

        keycloak: KeycloakService = info.context["keycloak"]
        keycloak.assert_roles(["Admin"])

        updated_id = await self.write_service.update(
            product_id, input, token=keycloak.token
        )
        return CreatePayload(id=updated_id)

    async def delete_product(self, product_id: UUID, info: Info) -> bool:
        logger.debug("delete_product: id={}", product_id)

        keycloak: KeycloakService = info.context["keycloak"]
        keycloak.assert_roles(["Admin"])

        return await self.write_service.delete(product_id, token=keycloak.token)
