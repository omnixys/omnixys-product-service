import asyncio
from uuid import uuid4

from product.messaging.producer import KafkaProducerService
from product.tracing.trace_context import TraceContext
from product.tracing.trace_context_util import TraceContextUtil


async def send_test_event():
    # ➕ Dummy-TraceContext erzeugen
    trace_ctx = TraceContext(
        trace_id=uuid4().hex,
        span_id=uuid4().hex,
        parent_span_id=None,
    )

    # ➕ Test-Payload
    test_payload = {
        "content": "Testevent aus kafka_test_sender.py",
        "note": "Dies ist eine Testnachricht mit Trace-Headern",
    }

    # ➕ Kafka-Producer starten
    producer = KafkaProducerService()
    await producer.start()

    # ➕ Testevent senden (z. B. an „orders.cancelled“)
    await producer.publish(
        topic="orders.cancelled",
        payload=test_payload,
        trace_ctx=trace_ctx,
    )

    # ➕ Producer wieder stoppen
    await producer.stop()

    print(f"✅ Testevent mit Trace-ID {trace_ctx.trace_id} gesendet.")


if __name__ == "__main__":
    asyncio.run(send_test_event())
