# src/product/otel_setup.py

from loguru import logger
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from product.config import env
from product.config.kafka import get_kafka_settings

# 🔧 Prometheus Setup
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.prometheus import PrometheusMetricReader

from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware

# 🔧 Prometheus ASGI App (z. B. für FastAPI)
from prometheus_client import make_asgi_app

from product.tracing.trace_context_middleware import TraceContextMiddleware


# Optional: in FastAPI verwenden
# metrics_app = make_asgi_app()  # app.mount("/metrics", metrics_app)

# def setup_otel():
#     """Initialisiert OpenTelemetry für Tempo (Tracing) und Prometheus (Metrics)."""
#     settings = get_kafka_settings()

#     # 🌐 Ressource definieren (Service-Name)
#     resource = Resource.create({SERVICE_NAME: settings.client_id})

#     # 🔹 Tracing (Tempo via OTLP HTTP)
#     tracer_provider = TracerProvider(resource=resource)
#     trace.set_tracer_provider(tracer_provider)

#     otlp_exporter = OTLPSpanExporter(endpoint="http://tempo:4318/v1/traces")
#     tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

#     # 🔸 Metrics (Prometheus)
#     prometheus_reader = PrometheusMetricReader()
#     meter_provider = MeterProvider(
#         resource=resource,
#         metric_readers=[prometheus_reader],
#     )
#     set_meter_provider(meter_provider)


def setup_otel(app):
    resource = Resource(attributes={SERVICE_NAME: get_kafka_settings().client_id})

    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    try:
        otlp_exporter = OTLPSpanExporter(
            # endpoint="http://tempo:4318",
            # endpoint="http://localhost:3200/v1/traces"
            endpoint="http://localhost:4318/v1/traces"
        )
    except Exception as e:
        logger.warning("Tempo Exporter konnte nicht gestartet werden: {}", str(e))

    span_processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(span_processor)

    # Instrumentiere FastAPI und MongoDB
    FastAPIInstrumentor().instrument_app(app)
    PymongoInstrumentor().instrument()

    # 🛠 TraceContextMiddleware aktivieren
    app.add_middleware(TraceContextMiddleware)
    app.add_middleware(OpenTelemetryMiddleware)
