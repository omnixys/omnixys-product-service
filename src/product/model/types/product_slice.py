from typing import List

import strawberry
from product.model.entity.product import ProductType


@strawberry.type
class ProductSlice:
    content: List[ProductType]
    total: int
    page: int
    size: int
