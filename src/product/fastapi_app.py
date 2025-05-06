# src/product/fastapi_app.py
"""MainApp."""

from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Final

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import FileResponse
from loguru import logger

from product.config import dev, env
from product.config.dev.db_populate_router import router as db_populate_router
from product.config.dev.db_populate import mongo_populate
from product.config.mongo import init_mongo
from product.error.exceptions import NotAllowedError, NotFoundError, VersionOutdatedError
from product.graphql.schema import graphql_router
from product.messaging.kafka_singleton import get_kafka_consumer, get_kafka_producer
from product.otel_setup import setup_otel
from product.repository.session import dispose_connection_pool
from product.router import health_router, shutdown_router

from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
from prometheus_fastapi_instrumentator import Instrumentator

from product.security.keycloak_service import KeycloakService

from .banner import banner

__all__ = [
    "authorization_error_handler",
    "email_exists_error_handler",
    "login_error_handler",
    "not_allowed_error_handler",
    "not_found_error_handler",
    "username_exists_error_handler",
    "version_outdated_error_handler",
]


TEXT_PLAIN: Final = "text/plain"

# --------------------------------------------------------------------------------------
# S t a r t u p   u n d   S h u t d o w n
# --------------------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:  # noqa: RUF029
    """Startup/Shutdown-Logik: MongoDB, Kafka, Banner."""
    logger.info("→ Starting up services…")
    await init_mongo()
    kafka_consumer = get_kafka_consumer()
    kafka_producer = get_kafka_producer()

    # Kein logger_plus im Producer während Start verwenden!


    logger.info("Starte Kafka Producer…")
    await kafka_producer.start()
    await kafka_consumer.start()
    if dev:
        await mongo_populate()
    banner(app.routes)
    yield
    logger.info("← Shutting down services…")
    await kafka_producer.stop()
    await kafka_consumer.stop()
    logger.info("Der Server wird heruntergefahren")
    await dispose_connection_pool()

if env.APP_ENV == "development":
    app: Final = FastAPI(lifespan=lifespan, debug=True)
else:
    app: Final = FastAPI(lifespan=lifespan)

# Setup Observability
setup_otel(app)  # Tracing mit Tempo
Instrumentator().instrument(app).expose(app)  # Prometheus-Metriken

# --------------------------------------------------------------------------------------
# R E S T
# --------------------------------------------------------------------------------------
app.include_router(health_router, prefix="/health")
app.include_router(shutdown_router, prefix="/admin")
if dev:
    app.include_router(db_populate_router, prefix="/dev")


# --------------------------------------------------------------------------------------
# G r a p h Q L
# --------------------------------------------------------------------------------------
app.include_router(graphql_router, prefix="/graphql")

# --------------------------------------------------------------------------------------
# F a v i c o n
# --------------------------------------------------------------------------------------
# @app.get("/favicon.ico")
# def favicon() -> FileResponse:
#     """facicon.ico ermitteln.

#     :return: Response-Objekt mit favicon.ico
#     :rtype: FileResponse
#     """
#     src_path: Final = Path("src")
#     file_name: Final = "favicon.ico"
#     favicon_path: Final = Path("product") / "static" / file_name
#     file_path: Final = src_path / favicon_path if src_path.is_dir() else favicon_path
#     logger.debug("file_path={}", file_path)
#     return FileResponse(
#         path=file_path,
#         headers={"Content-Disposition": f"attachment; filename={file_name}"},
#     )


@app.middleware("http")
async def inject_keycloak(request: Request, call_next):
    request.state.keycloak = await KeycloakService.create(request)
    response = await call_next(request)
    return response


# --------------------------------------------------------------------------------------
# E x c e p t i o n   H a n d l e r
# --------------------------------------------------------------------------------------
@app.exception_handler(NotFoundError)
def not_found_error_handler(_request: Request, _err: NotFoundError) -> Response:
    """Errorhandler für NotFoundError.

    :param _err: NotFoundError aus der Geschäftslogik
    :return: Response mit Statuscode 404
    :rtype: Response
    """
    return Response(status_code=status.HTTP_404_NOT_FOUND, media_type=TEXT_PLAIN)


@app.exception_handler(NotAllowedError)
def not_allowed_error_handler(_request: Request, _err: NotAllowedError) -> Response:
    """Errorhandler für NotAllowedError.

    :param _err: NotAllowedError vom Überprüfen der erforderlichen Rollen
    :return: Response mit Statuscode 401
    :rtype: Response
    """
    return Response(status_code=status.HTTP_401_UNAUTHORIZED, media_type=TEXT_PLAIN)


@app.exception_handler(VersionOutdatedError)
def version_outdated_error_handler(
    _request: Request,
    _err: VersionOutdatedError,
) -> Response:
    """Exception-Handling für VersionOutdatedError.

    :param _err: Exception, falls die Versionsnummer zum Aktualisieren veraltet ist
    :return: Response mit Statuscode 412
    :rtype: Response
    """
    return Response(
        status_code=status.HTTP_412_PRECONDITION_FAILED,
        media_type="application/json",
    )
