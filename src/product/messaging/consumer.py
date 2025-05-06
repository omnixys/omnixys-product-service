import asyncio
import json
from typing import Awaitable, Callable, Final, Optional

from aiokafka import AIOKafkaConsumer
from aiokafka.structs import ConsumerRecord
from loguru import logger
from opentelemetry import trace

from product.config.kafka import get_kafka_settings
from product.tracing.trace_context_util import TraceContextUtil


class KafkaConsumerService:
    """Asynchroner Kafka‑Consumer mit TraceContext und LoggerPlus."""

    def __init__(
        self,
        topics: list[str],
        group_id: Optional[str] = None,
        handlers: Optional[dict[str, Callable[[dict], Awaitable[None]]]] = None,
    ) -> None:
        self._consumer: Optional[AIOKafkaConsumer] = None
        self._task: Optional[asyncio.Task] = None
        settings = get_kafka_settings()
        self._bootstrap = settings.bootstrap_servers
        self._group_id = group_id
        self._topics: Final[list[str]] = topics
        self._handlers = handlers or {}
        self._handlers["gateway.shutdown-all"] = self._handle_shutdown
        self._log = logger.bind(classname=self.__class__.__name__)

    async def start(self) -> None:
        """Consumer starten und Nachrichten-Loop im Hintergrund-Task."""
        if self._consumer is not None:
            return
        self._log.info("🎧 Starte Kafka Consumer für Topics: {}", self._topics)
        self._consumer = AIOKafkaConsumer(
            *self._topics,
            bootstrap_servers=self._bootstrap,
            group_id=self._group_id,
            enable_auto_commit=True,
        )
        await self._consumer.start()
        # loop in separatem Task, damit shutdown clean geht
        self._task = asyncio.create_task(self._consume_loop())

    async def stop(self) -> None:
        """Consumer-Loop beenden und Consumer stoppen."""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._consumer:
            self._log.info("Stoppe Kafka Consumer…")
            await self._consumer.stop()
            self._consumer = None
            self._log.info("🛑 Kafka Consumer gestoppt")

    async def _consume_loop(self) -> None:
        """Liest Nachrichten und leitet an Handler weiter."""
        assert self._consumer is not None
        async for msg in self._consumer:
            await self._handle_message(msg)

    async def _handle_message(self, msg: ConsumerRecord) -> None:
        """Einzelne Nachricht verarbeiten."""
        try:
            # 🔁 TraceContext aus Kafka-Headern extrahieren
            trace_ctx, otel_ctx = TraceContextUtil.from_kafka_headers(msg.headers)
            TraceContextUtil.set(trace_ctx)

            tracer = trace.get_tracer("product.kafka")

            # ⬇️ Span für diese Verarbeitung starten
            with tracer.start_as_current_span(
                f"kafka.consume.{msg.topic}", context=otel_ctx
            ) as span:
                span.set_attribute("messaging.system", "kafka")
                span.set_attribute("messaging.destination", msg.topic)
                span.set_attribute("messaging.operation", "receive")
                span.set_attribute("messaging.messaging.partition", msg.partition)
                span.set_attribute("messaging.messaging.offset", msg.offset)
                span.set_attribute("messaging.messaging.consumer_group", self._group_id)

                log = self._log.bind(trace_id=trace_ctx.trace_id)
                self._log.debug(
                    "📨 Kafka-Event empfangen: Topic=%s Offset=%s",
                    msg.topic,
                    msg.offset,
                )
                try:
                    payload = json.loads(msg.value.decode("utf-8"))
                except json.JSONDecodeError:
                    log.error("❌ Ungültiges JSON: {}", msg.value)
                    return

                log.info(
                    "📨 Event empfangen: {} [Partition={}, Offset={}]",
                    msg.topic,
                    msg.partition,
                    msg.offset,
                )
                log.debug("→ Payload: {}", payload)

                handler = self._handlers.get(msg.topic)
                if handler:
                    # ⬇️ Optional: Sub-Span für Handler
                    with tracer.start_as_current_span(
                        f"handler.{msg.topic}", context=otel_ctx
                    ):
                        await handler(payload)
                else:
                    log.warning("⚠️ Kein Handler für Topic {}", msg.topic)

        except Exception as err:
            self._log.exception("Fehler beim Verarbeiten der Kafka‑Nachricht: %s", err)

    async def handle_log(self, event: dict):
            """Verarbeitet empfangene Kafka-Events."""
            event_type = event.get("event") or event.get("type")  # robust für verschiedene Schemas

            if event_type == "shutdown":
                logger.warning("⚠️ Shutdown-Event empfangen! Anwendung wird beendet.")
                await self.shutdown_application()
            else:
                # Normaler Logprozess
                logger.info(f"📝 Log-Eintrag: {event}")

    async def shutdown_application(self):
            """Führt einen geregelten Shutdown der FastAPI-Anwendung durch."""
            await self.stop()  # zuerst Kafka-Consumer stoppen
            loop = asyncio.get_event_loop()
            loop.call_later(1, loop.stop)  # sanfter Stop (optional: os._exit(0))

    async def _handle_shutdown(self, event: dict) -> None:
        self._log.warning("⚠️ Shutdown-Event empfangen. Beende Anwendung …")
        await self.shutdown_application()

