# src/product/model/entity/product.py

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Optional, List
from uuid import UUID, uuid4

from bson import Decimal128
import strawberry
from beanie import Document, Indexed
from pydantic import BaseModel, Field, field_validator

from product.model.entity.product_variant import ProductVariant, ProductVariantInput, ProductVariantType
from product.model.enum.product_category import ProductCategory


class Product(Document):
    """MongoDB-Dokument zur Repräsentation eines Produkts."""

    id: UUID = Field(default_factory=uuid4)
    name: Annotated[str, Indexed(unique=True)] = Field(..., description="Produktname")
    brand: Optional[str] = Field(None, description="Hersteller- oder Markenname")
    price: Decimal = Field(..., description="Grundpreis in Euro")
    description: Optional[str] = Field(None, description="Produktbeschreibung")
    category: ProductCategory = Field(..., description="Zugeordnete Produktkategorie")
    tags: List[str] = Field(default_factory=list, description="Tags zur Klassifikation")
    image_paths: List[str] = Field(default_factory=list, description="Pfad zu Bildern")
    variants: List[ProductVariant] = Field(default_factory=list)
    created: datetime = Field(default_factory=datetime.utcnow)
    updated: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("price", mode="before")
    @classmethod
    def convert_price_decimal128(cls, v):
        if isinstance(v, Decimal128):
            return v.to_decimal()
        return v


    class Settings:
        name = "products"
        use_revision = True
        indexes = ["name"]

    class Config:
        json_schema_extra = {
            "example": {
                "name": "iPhone 15",
                "brand": "Apple",
                "description": "Neueste Smartphone-Generation",
                "category": "ELEKTRONIK",
                "price": 999.99,
                "tags": ["smartphone", "apple", "highend"],
                "image_paths": ["img/iphone-15-front.png", "img/iphone-15-back.png"],
                "variants": [
                    {"name": "Farbe", "value": "Schwarz", "additional_price": 0},
                    {"name": "Speicher", "value": "256 GB", "additional_price": 100},
                ],
            }
        }


@strawberry.type
class ProductType:
    id: strawberry.ID
    name: str
    brand: Optional[str]
    price: float
    description: Optional[str]
    category: ProductCategory
    image_paths: List[str]
    variants: List[ProductVariantType]
    tags: Optional[List[str]]
    created: datetime
    updated: datetime


@strawberry.input
class ProductInput:
    """
    Eingabestruktur für das Anlegen oder Aktualisieren eines Produkts.
    """

    name: str
    brand: Optional[str] = None
    price: Decimal
    description: Optional[str] = None
    category: ProductCategory
    tags: Optional[List[str]] = None
    image_paths: Optional[List[str]] = None
    variants: Optional[List[ProductVariantInput]] = None


def map_product_to_product_type(product: Product) -> ProductType:
    """
    Wandelt ein MongoDB-Produktdokument in einen GraphQL-Produkttyp (`ProductType`) um.

    :param product: Produktdokument aus der Datenbank
    :return: GraphQL-kompatibler Produktdatentyp (`ProductType`)
    """
    return ProductType(
        id=str(product.id),
        name=product.name,
        brand=product.brand or "",
        price=float(product.price),
        description=product.description,
        category=ProductCategory(product.category),
        image_paths=product.image_paths or [],
        variants=[
            ProductVariantType(
                name=v.name,
                value=v.value,
                additional_price=float(v.additional_price or 0),
            )
            for i, v in enumerate(product.variants or [])
        ],
        tags=product.tags or [],
        created=product.created,
        updated=product.updated,
    )
