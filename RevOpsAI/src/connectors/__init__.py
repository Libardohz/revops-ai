"""Outbound connectors and protocols for RevOpsAI delivery."""

from RevOpsAI.src.connectors.base import DeliveryResult, OutboundConnector
from RevOpsAI.src.connectors.email_connector import EmailConnector, EmailTransport
from RevOpsAI.src.connectors.whatsapp_connector import WhatsAppCloudConnector

__all__ = [
    "DeliveryResult",
    "OutboundConnector",
    "EmailConnector",
    "EmailTransport",
    "WhatsAppCloudConnector",
]
