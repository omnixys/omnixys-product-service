"""Modul für den Anwendungskern."""

from product.error.exceptions import (
    EmailExistsError,
    NotAllowedError,
    NotFoundError,
    UsernameExistsError,
    VersionOutdatedError,
)

__all__ = [
    "EmailExistsError",
    "NotAllowedError",
    "NotFoundError",
    "UsernameExistsError",
    "VersionOutdatedError",
]
