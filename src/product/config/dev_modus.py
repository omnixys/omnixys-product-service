"""Konfiguration für den Entwicklungsmodus."""

from typing import Final

from product.config.config import product_config

__all__ = ["dev"]


_dev_toml: Final = product_config.get("dev", {})

dev: Final[bool] = bool(_dev_toml.get("enabled", False))
"""Flag, ob der Entwicklungsmodus aktiviert ist."""
