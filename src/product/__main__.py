"""CLI-Einstiegspunkt für das Projekt, z.B. über `python -m product`."""

from product.asgi_server import run

__all__ = ["run"]

if __name__ == "__main__":
    run()
