from typing import Protocol, runtime_checkable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from RevOpsAI.src.core.models import Prospect

@dataclass
class DeliveryResult:
    success: bool
    message_id: str
    error: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@runtime_checkable
class OutboundConnector(Protocol):
    def send(self, lead: Prospect, **kwargs) -> DeliveryResult:
        ...
