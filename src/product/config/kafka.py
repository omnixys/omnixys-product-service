from pydantic_settings import BaseSettings

from product.config import env


class KafkaSettings(BaseSettings):
    bootstrap_servers: str = env.KAFKA_URI
    topic_product_created: str = "product.created"
    topic_log: str = "activity.product.log"
    client_id: str = env.PROJECT_NAME

    class Config:
        env_prefix = "KAFKA_"


def get_kafka_settings() -> KafkaSettings:
    return KafkaSettings()
