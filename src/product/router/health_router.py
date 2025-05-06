# src/product/router/health_router.py

from typing import Any, Final
from fastapi import APIRouter
from product.repository.healthcheck import check_db_connection

__all__ = ["router"]

router: Final = APIRouter(tags=["Health"])


@router.get("/liveness")
def liveness() -> dict[str, Any]:
    """Überprüfen der Liveness."""
    return {"status": "up"}


@router.get("/readiness")
async def readiness() -> dict[str, Any]:
    """Überprüfen der Readiness."""
    db_status: Final = "up" if await check_db_connection() else "down"
    return {"db": db_status}
