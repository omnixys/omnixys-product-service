from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel

from product.messaging.dto.kafka_serializer_mixin import KafkaSerializerMixin
from product.tracing.trace_context import TraceContext


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class LogEventDTO(KafkaSerializerMixin):
    """Standardisiertes DTO für zentrale Log-Nachrichten über Kafka."""

    id: UUID = uuid4()
    timestamp: datetime = datetime.utcnow()
    level: LogLevel
    message: str
    service: str
    class_name: Optional[str] = None
    method_name: Optional[str] = None
