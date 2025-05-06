from typing import Optional
from pydantic import BaseModel
import strawberry


class CreatePayload(BaseModel):
    """
    DTO zur Rückgabe der erstellten Entitäts-ID für interne Verarbeitung oder Tests.
    """

    id: str
    message: Optional[str]
    error_code: Optional[str]


@strawberry.type
class CreatePayloadType:
    """
    GraphQL-Rückgabetyp für Mutations wie `create_product`, `add_variant` etc.
    """

    id: strawberry.ID
