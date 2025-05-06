# src/product/model/input/pagination.py

import strawberry


@strawberry.input
class PaginationInput:
    """GraphQL Input-Typ für Pagination."""

    skip: int = 0
    limit: int = 10
