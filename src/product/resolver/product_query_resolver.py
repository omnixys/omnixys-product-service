from typing import Final, List, Sequence

from loguru import logger
from opentelemetry import trace
from strawberry.types import Info

from product.error.exceptions import NotFoundError
from product.model.entity.product import ProductType
from product.model.input.searchcriteria import ProductSearchCriteria
from product.repository.pageable import Pageable
from product.repository.slice import Slice
from product.security.keycloak_service import KeycloakService
from product.service.product_read_service import ProductReadService
from product.tracing.decorators import traced
from product.tracing.trace_context_util import TraceContextUtil

tracer = trace.get_tracer(__name__)


class ProductQueryResolver:
    """Resolver für GraphQL-Queries zum Abrufen von Produkten."""

    def __init__(self, read_service: ProductReadService):
        self.read_service = read_service

    @traced("resolve_product")
    async def resolve_product(self, info: Info, product_id: str) -> ProductType | None:
        # with tracer.start_as_current_span("resolver.product"):
        logger.debug("resolve_product: product_id={}", product_id)

        # Rollenprüfung via Keycloak
        keycloak: KeycloakService = info.context["keycloak"]
        keycloak.assert_roles(["Admin", "User"])

        try:
            return await self.read_service.find_by_id(product_id)
        except NotFoundError:
            logger.warning("Kein Produkt gefunden für ID: %s", product_id)
            return None

    async def resolve_products(
        self,
        info: Info,
        pageable: Pageable,
        search_criteria: ProductSearchCriteria | None = None,
    ) -> Slice:
        logger.debug("resolve_products: search_criteria=%s", search_criteria)

        keycloak: KeycloakService = info.context["keycloak"]
        keycloak.assert_roles(["Admin", "User"])

        # Filter leere Felder heraus
        criteria_dict: Final = dict(vars(search_criteria)) if search_criteria else {}
        filtered: Final = {key: val for key, val in criteria_dict.items() if val}

        try:

            if not filtered:
                result_slice = await self.read_service.find_all(pageable)

            else:
                result_slice = await self.read_service.find_filtered(
                    filter_dict=filtered,
                    pageable=pageable,
                )

        except NotFoundError:
            logger.info("Keine Produkte gefunden mit Kriterien: %s", filtered)
            return []

        logger.debug("resolve_products: found=%d", len(result_slice.content))
        return result_slice
