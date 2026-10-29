import re
import httpx
from typing import Any
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.connectors.base import DeliveryResult

class WhatsAppCloudConnector:
    """Official WhatsApp Cloud API (Meta Graph API) outbound connector."""

    GRAPH_API_VERSION = "v21.0"

    def __init__(
        self,
        phone_number_id: str,
        access_token: str,
        http_client: Any | None = None,
    ):
        if not phone_number_id:
            raise ValueError("phone_number_id obligatorio")
        if not access_token:
            raise ValueError("access_token obligatorio")
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.http_client = http_client or httpx.Client(timeout=10.0)
        self.endpoint_url = f"https://graph.facebook.com/{self.GRAPH_API_VERSION}/{self.phone_number_id}/messages"

    def clean_phone_number(self, phone: str) -> str:
        # Strip all whitespace, dashes, parens
        cleaned = re.sub(r"[\s\-\(\)]", "", phone)
        if cleaned.startswith("+"):
            cleaned = cleaned[1:]
        if not re.match(r"^\d{9,15}$", cleaned):
            raise ValueError(f"Número de teléfono '{phone}' inválido para formato E.164")
        return cleaned

    def send_template(
        self,
        lead: Prospect,
        recipient_phone: str,
        template_name: str,
        language_code: str = "es",
        components: list[dict[str, Any]] | None = None,
    ) -> DeliveryResult:
        if lead.is_blacklisted:
            raise PermissionError(f"El prospecto {lead.id} está blacklisted.")
        if lead.state != ProspectState.APPROVED:
            raise ValueError(f"El prospecto {lead.id} no está en estado APPROVED (actual: {lead.state.value}).")

        target_phone = self.clean_phone_number(recipient_phone)

        payload = {
            "messaging_product": "whatsapp",
            "to": target_phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code},
                "components": components or [],
            },
        }

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        resp = self.http_client.post(self.endpoint_url, json=payload, headers=headers)
        if resp.status_code >= 400:
            return DeliveryResult(
                success=False,
                message_id="",
                error=f"WhatsApp API HTTP {resp.status_code}: {resp.text}"
            )

        data = resp.json()
        message_id = data.get("messages", [{}])[0].get("id", "")
        return DeliveryResult(success=True, message_id=message_id)

    def send(self, lead: Prospect, **kwargs) -> DeliveryResult:
        """Alias conforming to OutboundConnector protocol."""
        return self.send_template(lead=lead, **kwargs)
