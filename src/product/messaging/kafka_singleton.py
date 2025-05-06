# src/product/kafka/kafka_singleton.py

from functools import cache
from product.messaging.producer import KafkaProducerService
from product.messaging.consumer import KafkaConsumerService
from product.messaging.handlers.handlers import (
    handle_customer_created,
    handle_order_cancelled,
)

# Kein lru_cache, damit Start gesteuert werden kann
_kafka_producer_instance: KafkaProducerService | None = None
_kafka_consumer_instance: KafkaConsumerService | None = None


def get_kafka_producer() -> KafkaProducerService:
    global _kafka_producer_instance
    if _kafka_producer_instance is None:
        _kafka_producer_instance = KafkaProducerService()
    return _kafka_producer_instance


def get_kafka_consumer() -> KafkaConsumerService:
    global _kafka_consumer_instance
    if _kafka_consumer_instance is None:
        _kafka_consumer_instance = KafkaConsumerService(
            topics=["shopping-cart.customer.created", "orders.cancelled"],
            group_id="product-service-consumer",
            handlers={
                "shopping-cart.customer.created": handle_customer_created,
                "orders.cancelled": handle_order_cancelled,
            },
        )
    return _kafka_consumer_instance
