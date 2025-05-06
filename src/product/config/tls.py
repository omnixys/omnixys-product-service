"""Konfiguration für den privaten Schlüssel und das Zertifikat für TLS."""

from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Final

from loguru import logger

from product.config.config import product_config, resources_path

__all__ = ["tls_certfile", "tls_keyfile"]

_tls_toml: Final = product_config.get("tls", {})
_tls_path: Final[Path] = (Path(__file__).parent / "../../../../keys").resolve()

_key: Final[str] = _tls_toml.get("key", "key.pem")
tls_keyfile: Final[str] = str(_tls_path / _key)
logger.debug("private keyfile TLS: {}", tls_keyfile)

_certificate: Final[str] = _tls_toml.get("certificate", "certificate.crt")
tls_certfile: Final[str] = str(_tls_path / _certificate)
logger.debug("certfile TLS: {}", tls_certfile)
