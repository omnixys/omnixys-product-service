from loguru import logger
from opentelemetry import trace

from product.tracing.trace_context_util import TraceContextUtil


async def handle_customer_created(payload: dict) -> None:
    """
    Handler für das Topic `shopping-cart.customer.created`.
    Verarbeitet erstellte Kunden (Beispiel).
    """
    trace_ctx = TraceContextUtil.get()
    logger.info(
        "✅ Kunde erstellt empfangen (Trace-ID: {}): {}",
        trace_ctx.trace_id if trace_ctx else "–",
        payload,
    )
    # Beispiel: Hier könnte Logik folgen wie
    # - Customer speichern
    # - Product-Service updaten
    # - Benachrichtigung auslösen
    # await customer_service.save(payload)


async def handle_order_cancelled(payload: dict) -> None:
    """
    Handler für das Topic `orders.cancelled`.
    Erstellt optional einen eigenen Span und loggt TraceContext.
    """
    trace_ctx = TraceContextUtil.get()
    logger.warning(
        "🛑 Bestellung wurde storniert (Trace-ID: {}): {}",
        trace_ctx.trace_id if trace_ctx else "–",
        payload,
    )

    logger.warning(
        "🛑 Trace: {}",
        trace_ctx,
    )

    logger.warning("🧠 TraceContext im Handler: {}", trace_ctx)
