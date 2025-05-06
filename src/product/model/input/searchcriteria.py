# src/product/model/input/search_criteria.py

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

import strawberry
from pydantic import BaseModel

from product.model.enum.product_category import ProductCategory


class ProductSearchCriteria(BaseModel):
    """DTO für Produktsuche per Service, Repository oder API."""

    name: Optional[str] = None
    brand: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    product_category: Optional[ProductCategory] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    tags: Optional[List[str]] = None


@strawberry.input
class ProductSearchCriteriaInput:
    """GraphQL-Eingabeobjekt für Produktsuchanfragen."""

    name: Optional[str] = None
    brand: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    product_category: Optional[ProductCategory] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    tags: Optional[List[str]] = None
