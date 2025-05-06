"""
Modul-Deklaration für das Projekt als Namensraum und CLI-Einstiegspunkt.

Ermöglicht:
- Import als Python-Package: `from product import ...`
- Ausführung als Skript: `uv run product`
- Start per Uvicorn/Hypercorn z.B.:

    uvicorn src.product:app --reload --ssl-keyfile path --ssl-certfile path
"""

from product.asgi_server import run
from product.fastapi_app import app

__all__ = ["app", "main"]


def main() -> None:
    """Einstiegspunkt für CLI-Aufrufe via `uv run product`."""
    run()
