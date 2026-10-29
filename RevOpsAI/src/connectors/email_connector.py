from email.message import EmailMessage
from email.utils import formataddr, make_msgid
from typing import Protocol
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.connectors.base import DeliveryResult

class EmailTransport(Protocol):
    def send_mail(self, from_addr: str, to_addr: str, message_bytes: bytes) -> str:
        ...

class EmailConnector:
    """Outbound email delivery connector enforcing RFC compliance and legal anti-spam standards."""

    def __init__(
        self,
        from_address: str,
        sender_name: str = "RevOps AI",
        unsubscribe_url_base: str = "https://app.revops.ai/opt-out",
        transport: EmailTransport | None = None,
    ):
        if not from_address or "@" not in from_address:
            raise ValueError("from_address debe ser un correo válido")
        self.from_address = from_address
        self.sender_name = sender_name
        self.unsubscribe_url_base = unsubscribe_url_base
        self.transport = transport

    def send(
        self,
        lead: Prospect,
        recipient_email: str,
        subject: str,
        body: str,
    ) -> DeliveryResult:
        if lead.is_blacklisted:
            raise PermissionError(f"El prospecto {lead.id} está blacklisted. Envío cancelado.")
        if lead.state != ProspectState.APPROVED:
            raise ValueError(f"El prospecto {lead.id} no está en estado APPROVED (actual: {lead.state.value}).")
        if not recipient_email or "@" not in recipient_email:
            raise ValueError("recipient_email inválido")

        unsub_link = f"{self.unsubscribe_url_base}?tenant={lead.tenant_id}&lead={lead.id}"
        
        msg = EmailMessage()
        msg["From"] = formataddr((self.sender_name, self.from_address))
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg["Message-ID"] = make_msgid(domain=self.from_address.split("@")[-1])
        
        # Mandatory anti-spam RFC 8058 headers
        msg["List-Unsubscribe"] = f"<{unsub_link}>"
        msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
        
        # Disclaimers appended to message
        full_content = (
            f"{body}\n\n"
            f"---\n"
            f"Aviso Legal: Esta comunicación comercial es consultiva y dirigida a profesionales. "
            f"Para no recibir más comunicaciones, haga clic aquí: {unsub_link}"
        )
        msg.set_content(full_content)

        if not self.transport:
            return DeliveryResult(success=True, message_id=msg["Message-ID"])

        msg_id = self.transport.send_mail(
            from_addr=self.from_address,
            to_addr=recipient_email,
            message_bytes=msg.as_bytes(),
        )
        return DeliveryResult(success=True, message_id=msg_id)
