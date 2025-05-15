from typing import Final, List

import strawberry
from fastapi import Request
from strawberry.fastapi import GraphQLRouter
from strawberry.federation import Schema

from product.config.graphql import graphql_ide
from product.dependency_provider import (
    get_product_mutation_resolver,
    get_product_query_resolver,
)
from product.error.exceptions import AuthenticationError
from product.model.entity.product import ProductInput, ProductType
from product.model.entity.product_variant import ProductVariantInput
from product.model.input.pagination import PaginationInput
from product.model.input.searchcriteria import (
    ProductSearchCriteria,
    ProductSearchCriteriaInput,
)
from product.model.payload.create_payload import CreatePayload
from product.model.types.product_slice import ProductSlice
from product.repository.pageable import Pageable
from product.security.keycloak_service import KeycloakService


# Kontextbereitstellung
async def get_context(request: Request) -> dict:
    return {
        "request": request,
        "keycloak": getattr(request.state, "keycloak", None),
    }


# ---------------------------
# GraphQL Query Definition
# ---------------------------
@strawberry.type
class Query:
    @strawberry.field
    async def product(
        self,
        id: strawberry.ID,
        info: strawberry.types.Info = None,
    ) -> ProductType | None:
        keycloak: KeycloakService | None = info.context.get("keycloak")
        if keycloak is None:
            raise AuthenticationError()
        keycloak.assert_roles(["Admin", "User"])

        return await get_product_query_resolver().resolve_product(
            info, product_id=str(id)
        )

    @strawberry.field
    async def products(
        self,
        pagination: PaginationInput | None = None,
        search_criteria: ProductSearchCriteriaInput | None = None,
        info: strawberry.types.Info = None,
    ) -> ProductSlice:
        """Patienten anhand von Suchkriterien suchen.

        :param suchkriterien: nachname, email usw.
        :return: Die gefundenen Patienten
        :rtype: list[Patient]
        :raises NotFoundError: Falls kein Patient gefunden wurde, wird zu GraphQLError
        """

        keycloak: KeycloakService | None = info.context.get("keycloak")
        if keycloak is None:
            raise AuthenticationError()
        keycloak.assert_roles(["Admin", "User"])

        if pagination is None:
            pagination = PaginationInput(skip=0, limit=10)
        pageable = Pageable.create(skip=pagination.skip, limit=pagination.limit)

        # 💡 SearchCriteriaInput → SearchCriteria (DTO) umwandeln
        criteria = (
            ProductSearchCriteria(**search_criteria.__dict__)
            if search_criteria is not None
            else None
        )

        products = await get_product_query_resolver().resolve_products(
            info=info,
            pageable=pageable,
            search_criteria=criteria,
        )

        return ProductSlice(
            content=products.content,
            total=products.total,
            page=pageable.skip,
            size=pageable.limit,
        )


# ---------------------------
# GraphQL Mutation Definition
# ---------------------------
@strawberry.type
class Mutation:

    @strawberry.mutation
    async def create_product(
        self,
        input: ProductInput,
        info: strawberry.types.Info,
    ) -> CreatePayload:
        return await get_product_mutation_resolver().create_product(input, info)

    @strawberry.mutation
    async def add_variant(
        self,
        product_id: strawberry.ID,
        input: List[ProductVariantInput],
        info: strawberry.types.Info,
    ) -> CreatePayload:
        keycloak: KeycloakService | None = info.context.get("keycloak")
        if keycloak is None:
            raise AuthenticationError()
        keycloak.assert_roles(["Admin", "User"])

        return await get_product_mutation_resolver().add_variant(
            product_id, input, info
        )

    @strawberry.mutation
    async def add_image_paths(
        self,
        product_id: strawberry.ID,
        paths: List[str],
        info: strawberry.types.Info,
    ) -> CreatePayload:
        keycloak: KeycloakService | None = info.context.get("keycloak")
        if keycloak is None:
            raise AuthenticationError()
        keycloak.assert_roles(["Admin", "User"])

        return await get_product_mutation_resolver().add_image_paths(
            product_id, paths, info
        )

    @strawberry.mutation
    async def update_product(
        self,
        product_id: strawberry.ID,
        input: ProductInput,
        info: strawberry.types.Info,
    ) -> CreatePayload:
        keycloak: KeycloakService | None = info.context.get("keycloak")
        if keycloak is None:
            raise AuthenticationError()
        keycloak.assert_roles(["Admin", "User"])

        return await get_product_mutation_resolver().update_product(
            product_id, input, info
        )

    @strawberry.mutation
    async def delete_product(
        self,
        product_id: strawberry.ID,
        info: strawberry.types.Info,
    ) -> bool:
        keycloak: KeycloakService | None = info.context.get("keycloak")
        if keycloak is None:
            raise AuthenticationError()
        keycloak.assert_roles(["Admin", "User"])

        return await get_product_mutation_resolver().delete_product(product_id, info)


# ---------------------------
# Schema + Router
# ---------------------------
schema = Schema(
    query=Query,
    enable_federation_2=True,
)

graphql_router: Final = GraphQLRouter(
    schema,
    context_getter=get_context,
    graphql_ide=graphql_ide,
)
