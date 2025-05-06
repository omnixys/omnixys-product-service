# src/product/kafka/producer.py

import json
from typing import Final, Optional, Union

from aiokafka import AIOKafkaProducer
from loguru import logger
from opentelemetry import trace  # wichtig für Tracing
import orjson
from pydantic import BaseModel

from product.config import env
from product.config.kafka import get_kafka_settings
from product.logging.log_event_dto import LogEventDTO
from product.messaging.dto.kafka_message_dto import KafkaMessageDTO
from product.messaging.dto.kafka_serializer_mixin import KafkaSerializerMixin
from product.model.entity.product import Product
from product.tracing.trace_context import TraceContext
from product.tracing.trace_context_util import TraceContextUtil


class KafkaProducerService:
    """Kafka Producer mit automatischer TraceContext-Unterstützung und optionalen Headern."""

    def __init__(self) -> None:
        self._producer: Optional[AIOKafkaProducer] = None
        self.started: bool = False

        settings = get_kafka_settings()
        self._bootstrap = settings.bootstrap_servers
        self._client_id = settings.client_id
        self._topic_created: Final[str] = settings.topic_product_created

    async def start(self) -> None:
        if not self._producer:
            logger.info("🚀 Starte Kafka Producer…")
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self._bootstrap,
                client_id=self._client_id,
                acks="all",
                #value_serializer=self._serialize,
            )
            await self._producer.start()
            self.started = True
            logger.info("✅ Kafka Producer bereit")

    async def stop(self) -> None:
        if self._producer:
            logger.info("🛑 Stoppe Kafka Producer…")
            await self._producer.stop()
            self._producer = None
            self.started = False
            logger.info("Kafka Producer wurde gestoppt")

    async def publish(
        self,
        topic: str,
        payload: Union[KafkaSerializerMixin, dict],
        trace_ctx: Optional[TraceContext] = None,
        headers: Optional[list[tuple[str, str]]] = None,
    ) -> None:
        if not self.started or not self._producer:
            raise RuntimeError("Kafka Producer ist nicht gestartet")

        trace_ctx = trace_ctx or TraceContextUtil.get()
        kafka_headers: list[tuple[str, bytes]] = []

        logger.debug(
            "producer:  trace={}", trace_ctx
        )

        logger.debug(
            "Publishing to topic {}: {}", topic, payload, trace_context=trace_ctx
        )

        # Konvertiere TraceContext in Kafka-Header
        if trace_ctx:
            kafka_headers += [
                (k, v.encode()) for k, v in TraceContextUtil.to_headers(trace_ctx)
            ]

        if headers:
            kafka_headers += [(k, str(v).encode()) for k, v in headers]

        tracer = trace.get_tracer("product.kafka")

        # ⬇️ Neuer Span
        with tracer.start_as_current_span(f"kafka.publish.{topic}") as span:
            span.set_attribute("messaging.system", "kafka")
            span.set_attribute("messaging.destination", topic)
            span.set_attribute("messaging.operation", "send")
            span.set_attribute("messaging.messaging.client_id", self._client_id)
            span.set_attribute(
                "messaging.messaging.message_payload_size_bytes", len(str(payload))
            )

            logger.debug("📤 Sende Kafka-Event an '{}': {}", topic, payload)

            if hasattr(payload, "to_kafka"):
                value = payload.to_kafka()
            else:
                value = orjson.dumps(payload)


            await self._producer.send_and_wait(
                topic, value=value, headers=kafka_headers
            )

            logger.info(
                "✅ Event an '{}' gesendet (Trace-ID: {})",
                topic,
                trace_ctx if trace_ctx else "-",
            )

    async def publish_product_created(
        self, product: Product, trace_ctx: Optional[TraceContext] = None
    ) -> None:
        payload = {
            "event": "product_created",
            "product_id": str(product.id),
            "name": product.name,
            "brand": product.brand,
            "category": product.category.value,
            "price": float(product.price),
            "created_at": product.created_at.isoformat(),
        }
        await self.publish(self._topic_created, payload, trace_ctx)

    async def send_log_event(self, log_event: LogEventDTO, trace_ctx: TraceContext) -> None:
        await self.publish(
            topic="activity.product.logs",
            payload=log_event,
            trace_ctx=trace_ctx,
            headers=[
                ("x-service", self._client_id),
                ("x-event-name", "log"),
                ("x-event-version", "1.0.0"),
            ],
        )

    def _serialize(self, v: Union[dict, BaseModel]) -> bytes:
        try:
            if isinstance(v, BaseModel):
                return orjson.dumps(v.model_dump())
            if isinstance(v, dict):
                return orjson.dumps(v)
        except Exception as e:
            logger.exception("Fehler beim Serialisieren mit orjson")
            raise
        raise TypeError(f"Kann Typ {type(v)} nicht serialisieren")
