# src/product/metrics/metric_registry.py

from opentelemetry.metrics import get_meter
from opentelemetry.sdk.metrics import CallbackOptions
from opentelemetry.sdk.metrics.export import AggregationTemporality
from opentelemetry.sdk.metrics.view import View, ExplicitBucketHistogramAggregation

# 🔍 Meter (logisch gruppiert)
meter = get_meter("product.metrics")

# ➕ Counter für Produkt-Exporte
export_requests_counter = meter.create_counter(
    name="export_requests_total",
    description="Anzahl der Produkt-Exporte",
    unit="1",
)

# 📊 Histogramm für Dauer von DB-Abfragen
db_query_duration_histogram = meter.create_histogram(
    name="db_query_duration_seconds",
    description="Dauer von Produktabfragen in Sekunden",
    unit="s",
)

# Optional: weitere Histogram Bucket Konfiguration
custom_histogram_view = View(
    instrument_name="db_query_duration_seconds",
    aggregation=ExplicitBucketHistogramAggregation(
        boundaries=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0]
    ),
)
