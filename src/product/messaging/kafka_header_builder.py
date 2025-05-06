# src/product/kafka/kafka_header_builder.py

from typing import Final, Optional
from uuid import uuid4
from datetime import datetime

from product.config import env
from product.config.kafka import get_kafka_settings


class KafkaHeaderBuilder:
    """Erstellt standardisierte Kafka-Header inklusive Zipkin-Tracing-Informationen."""

    settings = get_kafka_settings()
    client_id = settings.client_id

    @staticmethod
    def build_headers(
        topic: str,
        event: str,
        version: str = "1.0.0",
        service: str = client_id,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
    ) -> list[tuple[str, bytes]]:
        """Erzeugt Kafka-Header inkl. Zipkin-Tracing.

        :param topic: Kafka-Topic.
        :param event: Event-Name.
        :param version: Event-Version.
        :param service: Absender-Service.
        :param trace_id: Zipkin Trace-ID (optional).
        :param span_id: Zipkin Span-ID (optional).
        :param parent_span_id: Optionaler Parent Span-ID.
        :return: Liste an Header-Tuples.
        """
        trace_id_final: Final = trace_id or uuid4().hex
        span_id_final: Final = span_id or uuid4().hex
        timestamp = datetime.utcnow().isoformat()

        headers: list[tuple[str, bytes]] = [
            ("x-service", service.encode()),
            ("x-event-name", event.encode()),
            ("x-event-version", version.encode()),
            ("x-topic", topic.encode()),
            ("x-timestamp", timestamp.encode()),
            # 🔁 Zipkin-kompatibel
            ("x-b3-traceid", trace_id_final.encode()),
            ("x-b3-spanid", span_id_final.encode()),
        ]

        if parent_span_id:
            headers.append(("x-b3-parentspanid", parent_span_id.encode()))

        return headers
