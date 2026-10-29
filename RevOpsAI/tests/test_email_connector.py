import pytest
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.connectors.email_connector import EmailConnector
from RevOpsAI.src.connectors.base import DeliveryResult

class MockEmailTransport:
    def __init__(self):
        self.sent_messages = []

    def send_mail(self, from_addr: str, to_addr: str, message_bytes: bytes) -> str:
        self.sent_messages.append({"from": from_addr, "to": to_addr, "raw": message_bytes})
        return "msg_mock_12345"

def test_email_connector_sends_email_with_compliance_headers():
    transport = MockEmailTransport()
    connector = EmailConnector(
        from_address="contacto@revops.clinicas.es",
        sender_name="Auditor Comercial Clínicas",
        transport=transport
    )
    
    lead = Prospect(
        tenant_id="tenant_dental",
        name="Clínica Dental Madrid",
        url="https://dentalmadrid.es",
        state=ProspectState.APPROVED
    )
    
    body = "Estimado equipo, detectamos oportunidades de optimización en su sitio web."
    result = connector.send(lead=lead, recipient_email="info@dentalmadrid.es", subject="Propuesta de Optimización Comercial", body=body)
    
    assert result.success is True
    assert result.message_id == "msg_mock_12345"
    assert len(transport.sent_messages) == 1
    
    raw = transport.sent_messages[0]["raw"].decode("utf-8")
    assert "List-Unsubscribe:" in raw
    assert "List-Unsubscribe-Post:" in raw
    assert "info@dentalmadrid.es" in transport.sent_messages[0]["to"]
    assert "contacto@revops.clinicas.es" in transport.sent_messages[0]["from"]

def test_email_connector_fails_if_lead_is_blacklisted():
    transport = MockEmailTransport()
    connector = EmailConnector(
        from_address="contacto@revops.clinicas.es",
        transport=transport
    )
    lead = Prospect(
        tenant_id="tenant_dental",
        name="Clínica Dental",
        url="https://dental.es",
        state=ProspectState.OPT_OUT,
        is_blacklisted=True
    )
    with pytest.raises(PermissionError, match="blacklisted"):
        connector.send(lead=lead, recipient_email="info@dental.es", subject="Test", body="Hola")

def test_email_connector_fails_if_lead_not_approved():
    transport = MockEmailTransport()
    connector = EmailConnector(
        from_address="contacto@revops.clinicas.es",
        transport=transport
    )
    lead = Prospect(
        tenant_id="tenant_dental",
        name="Clínica Dental",
        url="https://dental.es",
        state=ProspectState.RESEARCHING
    )
    with pytest.raises(ValueError, match="APPROVED"):
        connector.send(lead=lead, recipient_email="info@dental.es", subject="Test", body="Hola")
