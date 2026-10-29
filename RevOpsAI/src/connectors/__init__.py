"""Outbound connectors and protocols for RevOpsAI delivery."""

from RevOpsAI.src.connectors.base import DeliveryResult, OutboundConnector
from RevOpsAI.src.connectors.email_connector import EmailConnector, EmailTransport

__all__ = [
    "DeliveryResult",
    "OutboundConnector",
    "EmailConnector",
    "EmailTransport",
]
