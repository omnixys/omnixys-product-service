# src/product/core/dependency_provider.py

from functools import lru_cache
from product.messaging.consumer import KafkaConsumerService
from product.messaging.producer import KafkaProducerService
from product.repository.product_repository import ProductRepository
from product.resolver.product_mutation_resolver import ProductMutationResolver
from product.resolver.product_query_resolver import ProductQueryResolver
from product.service.product_read_service import ProductReadService
from product.service.product_write_service import ProductWriteService
from product.messaging.kafka_singleton import get_kafka_consumer, get_kafka_producer


@lru_cache()
def get_product_repository() -> ProductRepository:
    return ProductRepository()


@lru_cache()
def get_product_write_service() -> ProductWriteService:
    return ProductWriteService(
        repository=get_product_repository(), kafka_producer=get_kafka_producer()
    )


@lru_cache()
def get_product_read_service() -> ProductReadService:
    return ProductReadService(
        repository=get_product_repository()
    )

@lru_cache()
def get_product_query_resolver() -> ProductQueryResolver:
    return ProductQueryResolver(
        read_service=get_product_read_service()
    )

@lru_cache()
def get_product_mutation_resolver() -> ProductMutationResolver:
    return ProductMutationResolver(
        write_service=get_product_write_service()
    )


@lru_cache()
def get_kafka_consumer_singleton() -> KafkaConsumerService:
    return get_kafka_consumer()


@lru_cache()
def get_kafka_producer_singleton() -> KafkaProducerService:
    return get_kafka_producer()
