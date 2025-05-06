# src/product/model/enum/product_category.py

import strawberry
from enum import Enum


@strawberry.enum
class ProductCategory(Enum):
    """
    Kategorien zur Klassifikation von Produkten im Katalog.

    Diese Kategorien dienen zur besseren Filterung und Gruppierung
    von Produkten im Microservice.
    """

    ELEKTRONIK = "ELEKTRONIK"
    KLEIDUNG = "KLEIDUNG"
    BUECHER = "BUECHER"
    HAUSHALT = "HAUSHALT"
    SPIELWAREN = "SPIELWAREN"
    SPORT = "SPORT"
    BEAUTY = "BEAUTY"
    BUERO = "BUERO"
    LEBENSMITTEL = "LEBENSMITTEL"
    SONSTIGES = "SONSTIGES"
    ELECTRONICS = "ELECTRONICS"
    FRUIT_AND_VEGETABLES = "FRUIT_AND_VEGETABLES"
    FURNITURE = "FURNITURE"
    CLOTHING = "CLOTHING"
    TOYS = "TOYS"
