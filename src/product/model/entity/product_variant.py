# src/product/model/entity/product_variant.py

from __future__ import annotations

from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

import strawberry
from pydantic import BaseModel, Field, field_validator


class ProductVariant(BaseModel):
    """MongoDB-kompatibles Subdokument für eine Produktvariante."""

    name: str = Field(..., description="Name der Variante, z.B. 'Farbe'")
    value: str = Field(..., description="Wert der Variante, z.B. 'Rot'")
    additional_price: Optional[Decimal] = Field(
        default=0, description="Aufpreis für diese Variante"
    )

    @field_validator("additional_price", mode="before")
    @classmethod
    def convert_decimal128(cls, v):
        from bson.decimal128 import Decimal128

        if isinstance(v, Decimal128):
            return Decimal(str(v.to_decimal()))
        return v


@strawberry.type
class ProductVariantType:
    """GraphQL-Typ für eine Produktvariante."""

    name: str
    value: str
    additional_price: float


@strawberry.input
class ProductVariantInput:
    """
    GraphQL-Input-Typ für das Anlegen einer Produktvariante.
    Eingabestruktur für eine Produktvariante (z. B. Größe, Farbe).
    """

    name: str
    value: str
    additional_price: float
