"""
WaqediAI Observability Library

Provides structured logging, metrics, and distributed tracing
for all services.
"""

__version__ = "0.1.0"

from libs.observability.logging import configure_logging, get_logger
from libs.observability.metrics import MetricsClient, create_metrics_client
from libs.observability.tracing import TracingClient, create_tracing_client

__all__ = [
    "get_logger",
    "configure_logging",
    "MetricsClient",
    "create_metrics_client",
    "TracingClient",
    "create_tracing_client",
]
