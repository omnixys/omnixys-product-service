"""Modul für die GraphQL-Schnittstelle."""

from product.graphql.schema import Query, graphql_router, Mutation

__all__ = [
    "Query",
    "Mutation",
    "graphql_router",
]
