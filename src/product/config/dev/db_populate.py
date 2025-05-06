"""DEV: MongoDB mit Testdaten befüllen."""

from loguru import logger
from product.config.dev_modus import dev
from product.model.entity.product import Product
from product.model.entity.product_variant import ProductVariant
from product.model.enum.product_category import ProductCategory
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from bson.decimal128 import Decimal128
from pydantic import field_validator


def to_decimal(value: str) -> Decimal:
    return Decimal(str(Decimal128(value).to_decimal()))


# Optional: Central validator for ProductVariant (ensure compatibility)
ProductVariant.model_rebuild()


@field_validator("additional_price", mode="before")
def validate_additional_price(cls, v):
    if isinstance(v, Decimal128):
        return Decimal(str(v.to_decimal()))
    return v


setattr(ProductVariant, "validate_additional_price", validate_additional_price)


async def mongo_populate() -> None:
    """MongoDB mit Beispieldaten befüllen, falls im DEV-Modus."""
    if not dev:
        return

    logger.warning(">>> MongoDB wird im DEV-Modus befüllt <<<")

    await Product.delete_all()  # Achtung: löscht alles!

    sample_products = [
        Product(
            id=UUID("12000000-0000-0000-0000-000000000001"),
            name="Laptop",
            brand="ExampleBrand",
            price=to_decimal("999.99"),
            description="High-performance laptop",
            category=ProductCategory.ELEKTRONIK,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
        Product(
            id=UUID("12000000-0000-0000-0000-000000000002"),
            name="Smartphone",
            brand="AnotherBrand",
            price=to_decimal("499.99"),
            description="Latest smartphone response",
            category=ProductCategory.ELEKTRONIK,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
        Product(
            id=UUID("12000000-0000-0000-0000-000000000003"),
            name="Television",
            brand="AwesomeBrand",
            price=to_decimal("799.99"),
            description="4K Ultra HD Smart TV",
            category=ProductCategory.ELEKTRONIK,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
        Product(
            id=UUID("12000000-0000-0000-0000-000000000004"),
            name="Tablet",
            brand="YetAnotherBrand",
            price=to_decimal("299.99"),
            description="Portable tablet device",
            category=ProductCategory.ELEKTRONIK,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
        Product(
            id=UUID("12000000-0000-0000-0000-000000000005"),
            name="Smartwatch",
            brand="CoolBrand",
            price=to_decimal("199.99"),
            description="Fitness tracker smartwatch",
            category=ProductCategory.ELEKTRONIK,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
    ]

    for item in sample_products:
        await item.insert()

    product = Product(
        name="iPhone 15",
        brand="Apple",
        price=to_decimal("1199.99"),
        description="Neueste Generation des iPhone",
        category=ProductCategory.ELEKTRONIK,
        tags=["smartphone", "apple"],
        image_paths=["/img/iphone-front.png", "/img/iphone-back.png"],
        variants=[
            ProductVariant(
                name="Farbe", value="Schwarz", additional_price=to_decimal("0")
            ),
            ProductVariant(
                name="Speicher", value="256 GB", additional_price=to_decimal("100")
            ),
        ],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    await product.insert()

    logger.success("Beispieldaten wurden eingefügt.")
